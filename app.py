from flask import Flask, render_template, request, jsonify
import re
from PUEBIOfficialSplitter import PUEBIOfficialSplitter
from HybridSyllableSplitter import HybridSyllableSplitter
from SpellChecker import IndonesianSpellChecker
from KBBIScraper import KBBIScraper

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
