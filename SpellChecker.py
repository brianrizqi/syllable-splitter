# Indonesian Spell Checker with KBBI Validation
# Detects typos, validates against KBBI, and detects non-Indonesian words

import csv
import re
import os
from difflib import SequenceMatcher

class IndonesianSpellChecker:
    
    def __init__(self):
        """Initialize spell checker with KBBI word list."""
        self.kbbi_words = set()
        self._load_kbbi()
        
        # Common English words to detect non-Indonesian text
        self.common_english_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'hello', 'world', 'computer', 'learning', 'english', 'language'
        }
    
    def _load_kbbi(self):
        """Load KBBI word list from CSV file using built-in csv module."""
        try:
            kbbi_path = os.path.join(os.path.dirname(__file__), 'kbbi_v.csv')
            
            with open(kbbi_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # From looking at the CSV head, 'nama' seems to be the word column
                # Supporting multiple possible column names for robustness
                word_col = None
                if 'nama' in reader.fieldnames:
                    word_col = 'nama'
                elif 'lema' in reader.fieldnames:
                    word_col = 'lema'
                elif 'word' in reader.fieldnames:
                    word_col = 'word'
                
                if word_col:
                    for row in reader:
                        word = row[word_col]
                        if word:
                            self.kbbi_words.add(word.lower().replace('.', '').strip())
                else:
                    # Fallback to first column if no known header is found
                    first_col = reader.fieldnames[0]
                    for row in reader:
                        word = row[first_col]
                        if word:
                            self.kbbi_words.add(word.lower().replace('.', '').strip())
            
            print(f"✓ Loaded {len(self.kbbi_words)} words from KBBI")
            
        except Exception as e:
            print(f"⚠ Warning: Could not load KBBI CSV: {e}")
            print("  Spell checker will use pattern-based detection only")
            self.kbbi_words = set()
    
    def check_word(self, word):
        """
        Check if a word is spelled correctly.
        
        Args:
            word (str): Word to check
            
        Returns:
            dict: {
                'word': original word,
                'is_correct': boolean,
                'error_type': 'typo' | 'not_found' | 'non_indonesian' | None,
                'reason': explanation of the error,
                'suggestions': list of suggested corrections
            }
        """
        word_lower = word.lower()
        
        # Quick checks for obvious issues
        if len(word_lower) < 2:
            return {
                'word': word,
                'is_correct': True,
                'error_type': None,
                'reason': None,
                'suggestions': []
            }
        
        # Check for non-Indonesian patterns first
        non_indonesian_check = self._check_non_indonesian(word_lower)
        if non_indonesian_check:
            return {
                'word': word,
                'is_correct': False,
                'error_type': 'non_indonesian',
                'reason': non_indonesian_check,
                'suggestions': []
            }
        
        # Check for suspicious typo patterns
        typo_check = self._check_typo_patterns(word_lower)
        if typo_check:
            return {
                'word': word,
                'is_correct': False,
                'error_type': 'typo',
                'reason': typo_check,
                'suggestions': self._get_suggestions(word_lower)
            }
        
        # Check against KBBI if available
        if self.kbbi_words:
            if word_lower not in self.kbbi_words:
                return {
                    'word': word,
                    'is_correct': False,
                    'error_type': 'not_found',
                    'reason': 'Kata tidak ditemukan di KBBI',
                    'suggestions': self._get_suggestions(word_lower)
                }
        
        # Word is correct
        return {
            'word': word,
            'is_correct': True,
            'error_type': None,
            'reason': None,
            'suggestions': []
        }
    
    def _check_non_indonesian(self, word):
        """Check if word appears to be non-Indonesian."""
        # Check if it's a common English word
        if word in self.common_english_words:
            return 'Terdeteksi sebagai kata bahasa Inggris'
        
        # Check for non-Indonesian character patterns
        # Indonesian doesn't commonly use: q (except in loanwords), x, z (rare)
        if re.search(r'[qxf]', word) and len(word) > 3:
            # Exception: some loanwords are valid
            if self.kbbi_words and word in self.kbbi_words:
                return None
            return 'Mengandung huruf yang jarang digunakan dalam bahasa Indonesia'
        
        # Check for common English patterns
        english_patterns = [
            (r'tion$', 'Akhiran bahasa Inggris (-tion)'),
            (r'ing$', 'Akhiran bahasa Inggris (-ing)'),
            (r'^th', 'Awalan bahasa Inggris (th-)'),
            (r'ght', 'Pola bahasa Inggris (-ght-)'),
        ]
        
        for pattern, reason in english_patterns:
            if re.search(pattern, word):
                # Double check with KBBI
                if self.kbbi_words and word in self.kbbi_words:
                    return None
                return reason
        
        return None
    
    def _check_typo_patterns(self, word):
        """Check for obvious typo patterns."""
        suspicious_patterns = [
            (r'[bcdfghjklmnpqrstvwxyz]{5,}', 'Terlalu banyak konsonan berurutan'),
            (r'(.)\1{2,}', 'Karakter berulang berlebihan'),
            (r'^[bcdfghjklmnpqrstvwxyz]+$', 'Tidak ada vokal'),
        ]
        
        for pattern, reason in suspicious_patterns:
            if re.search(pattern, word):
                # Exception: very short words might be valid
                if len(word) <= 3 and pattern == suspicious_patterns[2][0]:
                    continue
                return reason
        
        return None
    
    def check_text(self, text):
        """
        Check multiple words in a text.
        
        Args:
            text (str): Text containing multiple words
            
        Returns:
            list: List of check results for incorrect words only
        """
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
        Get spelling suggestions using edit distance from KBBI.
        """
        if not self.kbbi_words:
            return self._get_pattern_suggestions(word)
        
        suggestions = []
        
        # Find similar words using edit distance
        for kbbi_word in self.kbbi_words:
            # Only consider words with similar length
            if abs(len(kbbi_word) - len(word)) > 2:
                continue
            
            # Calculate similarity
            similarity = SequenceMatcher(None, word, kbbi_word).ratio()
            
            if similarity > 0.7:  # 70% similar
                suggestions.append((kbbi_word, similarity))
        
        # Sort by similarity and return top 5
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in suggestions[:5]]
    
    def _get_pattern_suggestions(self, word):
        """Get suggestions based on common typo patterns."""
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
