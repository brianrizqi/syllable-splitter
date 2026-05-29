from flask import Flask, render_template, request, jsonify, send_file, make_response
import re
import csv
import io
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env or .env.local
load_dotenv()
from PUEBIOfficialSplitter import PUEBIOfficialSplitter
from HybridSyllableSplitter import HybridSyllableSplitter
from SpellChecker import IndonesianSpellChecker
from KBBIScraper import KBBIScraper
from SyllableValidationDB import SyllableValidationDB

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize splitters and other components with resilience
initialization_errors = []

try:
    splitter_puebi = PUEBIOfficialSplitter()
except Exception as e:
    initialization_errors.append(f"PUEBI Splitter: {e}")

try:
    splitter_sylbi = HybridSyllableSplitter()
except Exception as e:
    initialization_errors.append(f"SylBI Splitter: {e}")

try:
    kbbi_scraper = KBBIScraper()
except Exception as e:
    initialization_errors.append(f"KBBI Scraper: {e}")

try:
    spell_checker = IndonesianSpellChecker()
except Exception as e:
    initialization_errors.append(f"Spell Checker: {e}")

try:
    validation_db = SyllableValidationDB()
except Exception as e:
    initialization_errors.append(f"Validation DB: {e}")

if initialization_errors:
    print(f"⚠ Warning: Some components failed to initialize:\n" + "\n".join(initialization_errors))

def get_location_from_ip(ip: str):
    """Fetch city and country from IP using ip-api.com (free, no key required)."""
    if ip in ['127.0.0.1', 'localhost', '::1'] or not ip:
        return "Local", "Local"
    try:
        import requests
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data.get('city', 'Unknown'), data.get('country', 'Unknown')
    except Exception as e:
        print(f"Error fetching location mapping: {e}")
    return "Unknown", "Unknown"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok' if not initialization_errors else 'partial_failure',
        'errors': initialization_errors,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/split', methods=['POST'])
def split_text():
    data = request.get_json()
    text = data.get('text', '')
    method = data.get('method', 'puebi')  # Default to PUEBI
    bypass_db = data.get('bypass_db', False)  # Option to bypass database
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Split by whitespace and punctuation
    words = re.findall(r'\b[\w]+\b', text)
    
    results = []
    from_db_any = False
    
    for word in words:
        syllables = None
        from_db = False
        
        # 1. Check database first (if not bypassed)
        if not bypass_db:
            validation = validation_db.check_word_exists(word, method)
            if validation:
                syllables = validation['final_result'].split('-')
                from_db = True
                from_db_any = True
        
        # 2. If not found in DB or bypassed, use algorithms
        kbbi_info = []
        if syllables is None:
            if method == 'kbbi':
                kbbi_info = kbbi_scraper.get_word_info(word)
                if kbbi_info:
                    syllables = kbbi_info[0]['syllables']
                else:
                    syllables = splitter_puebi.split_syllables(word)
            elif method == 'sylbi':
                # Always try KBBI first to get all possible meanings and structures
                kbbi_info = kbbi_scraper.get_word_info(word)
                
                if kbbi_info:
                    # Improve entries by re-splitting them morphologically using extracted root hints
                    for entry in kbbi_info:
                        header = entry.get('header', '')
                        root_hint = None
                        
                        # Extract root hint from KBBI header
                        if ' » ' in header:
                            root_hint = header.split(' » ')[0].split('(')[0].strip().rstrip(' 0123456789')
                        elif '/' in header:
                            # If it's a base word (like 'beruang' bear), hint is the word itself
                            root_hint = word
                            
                        # Re-calculate syllables using SylBI with the specific root hint
                        if root_hint:
                            # Use syllable splitting logic with hint
                            entry['syllables'] = splitter_sylbi.split_syllables(word, root_hint=root_hint)
                            entry['root_hint'] = root_hint # Save for UI debug
                            
                    # Use the first entry's improved syllables as the base result
                    syllables = kbbi_info[0]['syllables']
                else:
                    # SylBI Fallback Logic:
                    # If not in KBBI online, use algorithms
                    syllables = splitter_sylbi.split_syllables(word)
            else:
                syllables = splitter_puebi.split_syllables(word)
        
        results.append({
            'word': word,
            'syllables': syllables,
            'from_db': from_db,
            'entries': kbbi_info
        })
    
    return jsonify({
        'results': results,
        'method': method,
        'from_db_any': from_db_any
    })

@app.route('/check_spelling', methods=['POST'])
def check_spelling():
    """Check text for potential typos and return suggestions."""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Check for typos in the text
    typos = spell_checker.check_text(text)
    
    return jsonify({
        'typos': typos,
        'has_typos': len(typos) > 0
    })

@app.route('/download-template', methods=['GET'])
def download_template():
    """Download CSV template for batch processing."""
    # Create CSV template
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['word', 'method'])
    
    # Write example rows
    writer.writerow(['pembelajaran', 'sylbi'])
    writer.writerow(['Indonesia', 'puebi'])
    writer.writerow(['membaca', 'sylbi'])
    writer.writerow(['komputer', 'puebi'])
    
    # Create response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='syllable_splitter_template.csv'
    )

@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    """Upload and process CSV file for batch syllable splitting."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode('utf-8'), newline=None)
        csv_reader = csv.DictReader(stream)
        
        # Check if required columns exist
        if 'word' not in csv_reader.fieldnames:
            return jsonify({'error': 'CSV must have a "word" column'}), 400
        
        results = []
        spell_check_enabled = request.form.get('spell_check', 'true').lower() == 'true'
        
        for row in csv_reader:
            word = row.get('word', '').strip()
            method = row.get('method', 'sylbi').strip().lower()
            
            if not word:
                continue
            
            # Validate method
            if method not in ['puebi', 'sylbi', 'kbbi']:
                method = 'sylbi'  # Default to sylbi
            
            # Spell check if enabled
            errors = []
            has_errors = False
            if spell_check_enabled:
                spell_errors = spell_checker.check_text(word)
                if spell_errors:
                    has_errors = True
                    errors = spell_errors
            
            # Process syllable splitting
            validation = validation_db.check_word_exists(word, method)
            if validation:
                syllables = validation['final_result'].split('-')
            else:
                if method == 'kbbi':
                    syllables = kbbi_scraper.get_syllables(word)
                    if syllables is None:
                        syllables = splitter_puebi.split_syllables(word)
                elif method == 'sylbi':
                    syllables = splitter_sylbi.split_syllables(word)
                else:
                    syllables = splitter_puebi.split_syllables(word)
            
            results.append({
                'word': word,
                'method': method,
                'syllables': syllables,
                'joined': '-'.join(syllables),
                'has_errors': has_errors,
                'errors': errors
            })
        
        return jsonify({
            'total': len(results),
            'processed': len(results),
            'results': results
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing CSV: {str(e)}'}), 500

@app.route('/export-results', methods=['POST'])
def export_results():
    """Export results as CSV file."""
    data = request.get_json()
    results = data.get('results', [])
    
    if not results:
        return jsonify({'error': 'No results to export'}), 400
    
    try:
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['word', 'method', 'syllables', 'joined', 'has_errors', 'error_details'])
        
        # Write results
        for result in results:
            error_details = ''
            if result.get('has_errors') and result.get('errors'):
                error_details = '; '.join([
                    f"{e['word']}: {e.get('reason', 'Error')}" 
                    for e in result['errors']
                ])
            
            writer.writerow([
                result.get('word', ''),
                result.get('method', ''),
                ', '.join(result.get('syllables', [])),
                result.get('joined', ''),
                'Yes' if result.get('has_errors') else 'No',
                error_details
            ])
        
        # Create response
        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'syllable_results_{timestamp}.csv'
        )
    
    except Exception as e:
        return jsonify({'error': f'Error exporting results: {str(e)}'}), 500

@app.route('/check_word_history', methods=['POST'])
def check_word_history():
    """Check if a word has been validated before."""
    data = request.get_json()
    word = data.get('word', '').strip()
    method = data.get('method', None)
    
    if not word:
        return jsonify({'error': 'No word provided'}), 400
    
    # Check if word exists in database
    validation = validation_db.check_word_exists(word, method)
    
    if validation:
        return jsonify({
            'exists': True,
            'validation': validation
        })
    else:
        return jsonify({
            'exists': False
        })

@app.route('/save_validation', methods=['POST'])
def save_validation():
    """Save a validation (correct or corrected) to the database."""
    data = request.get_json()
    word = data.get('word', '').strip()
    method = data.get('method', 'puebi')
    system_result = data.get('system_result', '')
    validation_type = data.get('validation_type', 'correct')  # 'correct' or 'corrected'
    final_result = data.get('final_result', '')
    
    if not word or not system_result or not final_result:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if validation_type not in ['correct', 'corrected']:
        return jsonify({'error': 'Invalid validation type'}), 400
    
    # Capture client IP and location
    client_ip = request.remote_addr
    # Handle X-Forwarded-For if behind a proxy like Vercel/Netlify
    if request.headers.get('X-Forwarded-For'):
        client_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        
    city, country = get_location_from_ip(client_ip)
    
    # Save to database
    success = validation_db.add_validation(
        word=word,
        method=method,
        system_result=system_result,
        validation_type=validation_type,
        final_result=final_result,
        ip=client_ip,
        city=city,
        country=country
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Validation saved successfully'
        })
    else:
        return jsonify({'error': 'Failed to save validation'}), 500

@app.route('/validation_stats', methods=['GET'])
def validation_stats():
    """Get validation database statistics."""
    stats = validation_db.get_statistics()
    return jsonify(stats)

@app.route('/database')
def view_database():
    records = validation_db.export_database()
    
    # Days and Months in Indonesian
    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    
    formatted_records = []
    for r in records:
        try:
            # Parse ISO timestamp
            dt = datetime.fromisoformat(r.get('timestamp', ''))
            
            # Formatted time: l, d F Y H:i:s -> "Selasa, 10 Maret 2026 10:47:22"
            day_name = days[dt.weekday()]
            month_name = months[dt.month - 1]
            formatted_time = f"{day_name}, {dt.day:02d} {month_name} {dt.year} {dt.strftime('%H:%M:%S')}"
            
            # Add raw date for JS filtering (YYYY-MM-DD)
            r['formatted_time'] = formatted_time
            r['raw_date'] = dt.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            r['formatted_time'] = r.get('timestamp', '')
            r['raw_date'] = ''
        formatted_records.append(r)
        
    # Sort by timestamp descending
    formatted_records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return render_template('database.html', records=formatted_records)

# Export app for Vercel/Netlify serverless functions
app_handle = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
