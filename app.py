from flask import Flask, render_template, request, jsonify
import re
from PUEBIOfficialSplitter import PUEBIOfficialSplitter
from HybridSyllableSplitter import HybridSyllableSplitter
from SpellChecker import IndonesianSpellChecker

app = Flask(__name__)

# Initialize both splitters
splitter_puebi = PUEBIOfficialSplitter()  # Official PUEBI rules
splitter_kbbi = HybridSyllableSplitter()  # Hybrid morphological splitter for KBBI
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
    
    # Select appropriate splitter based on method
    if method == 'kbbi':
        splitter = splitter_kbbi
    else:
        splitter = splitter_puebi
    
    # Split by whitespace and punctuation
    words = re.findall(r'\b[\w]+\b', text)
    
    results = []
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
