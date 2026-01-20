from flask import Flask, render_template, request, jsonify, send_file, make_response
import re
import csv
import io
from datetime import datetime
from PUEBIOfficialSplitter import PUEBIOfficialSplitter
from HybridSyllableSplitter import HybridSyllableSplitter
from SpellChecker import IndonesianSpellChecker
from KBBIScraper import KBBIScraper

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize three splitters
splitter_puebi = PUEBIOfficialSplitter()  # Official PUEBI rules
splitter_sylbi = HybridSyllableSplitter()  # Hybrid morphological splitter for SylBI
kbbi_scraper = KBBIScraper()  # KBBI scraper for online dictionary
spell_checker = IndonesianSpellChecker()  # Spell checker for typo detection

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/split', methods=['POST'])
def split_text():
    data = request.get_json()
    text = data.get('text', '')
    method = data.get('method', 'puebi')  # Default to PUEBI
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Split by whitespace and punctuation
    words = re.findall(r'\b[\w]+\b', text)
    
    results = []
    
    # Handle different methods
    if method == 'kbbi':
        # Use KBBI scraper (requires internet connection)
        for word in words:
            # Query KBBI online dictionary
            syllables = kbbi_scraper.get_syllables(word)
            
            # If KBBI lookup fails, fallback to PUEBI method
            if syllables is None:
                syllables = splitter_puebi.split_syllables(word)
            
            results.append({
                'word': word,
                'syllables': syllables
            })
    else:
        # Use local splitters (PUEBI or SylBI)
        if method == 'sylbi':
            splitter = splitter_sylbi
        else:
            splitter = splitter_puebi
        
        for word in words:
            syllables = splitter.split_syllables(word)
            results.append({
                'word': word,
                'syllables': syllables
            })
    
    return jsonify({
        'results': results,
        'method': method
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
