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
        if syllables is None:
            if method == 'kbbi':
                syllables = kbbi_scraper.get_syllables(word)
                if syllables is None:
                    syllables = splitter_puebi.split_syllables(word)
            elif method == 'sylbi':
                # SylBI Fallback Logic:
                # If word has morphological affixes or infixes, use SylBI (Hybrid) rules
                # If word is a base word (no affixes/infixes), follow KBBI rules (scraper)
                prefix, root, suffix = splitter_sylbi.morphology.analyze(word)
                internal_infix, _ = splitter_sylbi.morphology.analyze_internal_infix(word.lower())
                
                if not prefix and not suffix and not internal_infix:
                    # No affixes or infixes detected, try KBBI online first
                    syllables = kbbi_scraper.get_syllables(word)
                
                # If it has affixes/infixes OR KBBI online failed for base word
                if syllables is None:
                    syllables = splitter_sylbi.split_syllables(word)
            else:
                syllables = splitter_puebi.split_syllables(word)
        
        results.append({
            'word': word,
            'syllables': syllables,
            'from_db': from_db
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
    
    # Save to database
    success = validation_db.add_validation(
        word=word,
        method=method,
        system_result=system_result,
        validation_type=validation_type,
        final_result=final_result
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
    # Sort by timestamp descending
    records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return render_template('database.html', records=records)

# Export app for Vercel/Netlify serverless functions
app_handle = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
