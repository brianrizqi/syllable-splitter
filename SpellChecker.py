# Indonesian Spell Checker
# Detects typos and provides word suggestions

from spellchecker import SpellChecker

class IndonesianSpellChecker:
    
    def __init__(self):
        # Initialize spell checker with Indonesian language
        # Note: pyspellchecker doesn't have built-in Indonesian, 
        # so we'll use the word frequency from our lemmatizer
        self.spell = SpellChecker(language=None)  # Start with empty dictionary
        
        # We'll rely on nlp-id's vocabulary for now
        # In production, you could load a custom Indonesian word list
        self.use_nlp_id = True
        
        if self.use_nlp_id:
            try:
                from nlp_id.lemmatizer import Lemmatizer
                self.lemmatizer = Lemmatizer()
            except ImportError:
                self.use_nlp_id = False
    
    def check_word(self, word):
        """
        Check if a word is spelled correctly.
        
        Args:
            word (str): Word to check
            
        Returns:
            dict: {
                'word': original word,
                'is_correct': boolean,
                'suggestions': list of suggested corrections
            }
        """
        word_lower = word.lower()
        
        # Quick checks for obvious issues
        if len(word_lower) < 2:
            return {'word': word, 'is_correct': True, 'suggestions': []}
        
        # Check for suspicious patterns that are likely typos
        import re
        suspicious_patterns = [
            (r'[bcdfghjklmnpqrstvwxyz]{5,}', 'Terlalu banyak konsonan berurutan'),  # 5+ consonants
            (r'(.)\1{2,}', 'Karakter berulang'),  # Same character 3+ times
            (r'^[bcdfghjklmnpqrstvwxyz]+$', 'Tidak ada vokal'),  # No vowels (except for very short words)
        ]
        
        for pattern, reason in suspicious_patterns:
            if re.search(pattern, word_lower):
                # Exception: very short words might be valid
                if len(word_lower) <= 3 and pattern == suspicious_patterns[2][0]:
                    continue
                    
                return {
                    'word': word,
                    'is_correct': False,
                    'suggestions': self._get_suggestions(word_lower),
                    'reason': reason
                }
        
        # If no obvious typo patterns, assume it's correct
        # (lemmatizer is too permissive, so we only use pattern matching)
        return {
            'word': word,
            'is_correct': True,
            'suggestions': []
        }
    
    def check_text(self, text):
        """
        Check multiple words in a text.
        
        Args:
            text (str): Text containing multiple words
            
        Returns:
            list: List of check results for each word
        """
        # Split by whitespace and common punctuation
        import re
        words = re.findall(r'\b\w+\b', text)
        
        results = []
        for word in words:
            if len(word) > 1:  # Skip single characters
                result = self.check_word(word)
                if not result['is_correct']:
                    results.append(result)
        
        return results
    
    def _get_suggestions(self, word):
        """
        Get spelling suggestions for a misspelled word.
        Uses edit distance and common patterns.
        """
        # This is a simple implementation
        # In production, you'd want a proper Indonesian word list
        suggestions = []
        
        # Common typo patterns in Indonesian
        common_replacements = {
            'i': ['y', 'e'],
            'y': ['i'],
            'e': ['i', 'a'],
            'a': ['e'],
            'u': ['o'],
            'o': ['u'],
            'k': ['c', 'q'],
            'c': ['k'],
            's': ['z'],
            'z': ['s']
        }
        
        # Try single character replacements
        for i, char in enumerate(word):
            if char in common_replacements:
                for replacement in common_replacements[char]:
                    suggestion = word[:i] + replacement + word[i+1:]
                    if suggestion != word:
                        suggestions.append(suggestion)
        
        return suggestions[:5]

if __name__ == '__main__':
    # Test the spell checker
    checker = IndonesianSpellChecker()
    
    test_words = [
        'pembelajaran',  # correct
        'pmbelajaran',   # typo: missing 'e'
        'membaca',       # correct
        'mmbaca',        # typo: double 'm'
        'belajar',       # correct
        'blajar'         # typo: missing 'e'
    ]
    
    print('Spell Checker Test:')
    print('=' * 60)
    for word in test_words:
        result = checker.check_word(word)
        status = '✓' if result['is_correct'] else '✗'
        print(f'{status} {word:15} - Correct: {result["is_correct"]}')
        if result['suggestions']:
            print(f'  Suggestions: {", ".join(result["suggestions"])}')
