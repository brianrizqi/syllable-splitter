# Morphological Analyzer for Indonesian Language
# Detects prefixes, suffixes, and circumfixes

from nlp_id.lemmatizer import Lemmatizer

class MorphologicalAnalyzer:
    
    def __init__(self):
        # Initialize lemmatizer for accurate root detection
        self.lemmatizer = Lemmatizer()
        
        # Indonesian prefixes (sorted by length for greedy matching)
        self.prefixes = [
            # Complex prefixes (longest first for greedy matching)
            'memper', 'memper', 'diper', 'keber', 'terpem', 'terpe',
            'mempel', 'mempe', 'pember', 'penge', 'penge',
            # Nasal prefixes with variations
            'meng', 'meny', 'mem', 'men', 'me',
            'peng', 'peny', 'pem', 'pen', 'pe',
            # Other common prefixes
            'ber', 'ter', 'per', 'di', 'ke', 'se'
        ]
        
        # Indonesian suffixes (including particles and possessives)
        self.suffixes = [
            # Derivational suffixes
            'kan', 'an', 'i',
            # Particles
            'lah', 'kah', 'tah', 'pun',
            # Possessive pronouns
            'ku', 'mu', 'nya'
        ]
        
        # Circumfixes (prefix + suffix combinations)
        self.circumfixes = [
            # ke- + -an (nominalization)
            ('ke', 'an'),
            # pe- + -an (nominalization)
            ('pe', 'an'), ('pem', 'an'), ('pen', 'an'), ('peng', 'an'), ('peny', 'an'),
            # per- + -an (nominalization)
            ('per', 'an'),
            # ber- + -an (reciprocal/collective)
            ('ber', 'an'), ('ber', 'kan'),
            # me- + -kan/-i (transitive verbs)
            ('me', 'kan'), ('me', 'i'),
            ('mem', 'kan'), ('mem', 'i'),
            ('men', 'kan'), ('men', 'i'),
            ('meng', 'kan'), ('meng', 'i'),
            ('meny', 'kan'), ('meny', 'i'),
            # di- + -kan/-i (passive verbs)
            ('di', 'kan'), ('di', 'i'),
            # ter- + -kan (accidental passive)
            ('ter', 'kan'),
            # per- + -kan/-i (causative)
            ('per', 'kan'), ('per', 'i'),
            # se- + -nya (superlative)
            ('se', 'nya')
        ]
    
    def decompose_prefix(self, prefix):
        """
        Decompose a prefix into base prefix and infix.
        
        Indonesian prefixes like "pe", "be", "me" can have infixes inserted:
        - "pem", "pel", "per" → base "pe" + infix "m", "l", "r"
        - "bem", "bel", "ber" → base "be" + infix "m", "l", "r"
        - "mem", "mel", "mer" → base "me" + infix "m", "l", "r"
        
        Args:
            prefix: The prefix string to decompose
            
        Returns:
            tuple: (base_prefix, infix) where infix is empty string if no infix detected
        """
        if not prefix:
            return ('', '')
        
        # Define base prefixes that can have infixes
        base_prefixes = ['pe', 'be', 'me']
        # Common infixes inserted after base prefixes
        infixes = ['m', 'l', 'r', 'n', 'ng', 'ny']
        
        # Check if prefix is a variation with infix
        for base in base_prefixes:
            if prefix.startswith(base) and len(prefix) > len(base):
                potential_infix = prefix[len(base):]
                # Check if the remaining part is a valid infix
                if potential_infix in infixes:
                    return (base, potential_infix)
        
        # No infix detected, return prefix as-is
        return (prefix, '')
    
    def analyze(self, word):
        """
        Analyze word and return (prefix, root, suffix)
        
        Returns:
            tuple: (prefix, root, suffix) where each can be empty string
        """
        original_word = word.lower()
        prefix = ''
        suffix = ''
        root = word.lower()
        
        # Step 1: Check for circumfixes first (most specific)
        for pre, suf in self.circumfixes:
            if (root.startswith(pre) and root.endswith(suf) and 
                len(root) > len(pre) + len(suf)):
                potential_root = root[len(pre):-len(suf)]
                if len(potential_root) >= 2:  # Root should be at least 2 chars
                    prefix = pre
                    suffix = suf
                    root = potential_root
                    return (prefix, root, suffix)
        
        # Step 2: Check for prefixes
        for pre in sorted(self.prefixes, key=len, reverse=True):
            if root.startswith(pre) and len(root) > len(pre):
                potential_root = root[len(pre):]
                if len(potential_root) >= 2:
                    prefix = pre
                    root = potential_root
                    break
        
        # Step 3: Check for suffixes
        for suf in sorted(self.suffixes, key=len, reverse=True):
            if root.endswith(suf) and len(root) > len(suf):
                potential_root = root[:-len(suf)]
                if len(potential_root) >= 2:
                    suffix = suf
                    root = potential_root
                    break
        
        return (prefix, root, suffix)
    
    def analyze_with_lemmatizer(self, word):
        """
        Analyze word using nlp-id lemmatizer for accurate root detection.
        Uses pattern matching for prefix/suffix boundaries.
        
        Returns:
            tuple: (prefix, detected_root, suffix, lemmatized_root)
                  - detected_root: root with possible infixes (e.g., "mbelajar")
                  - lemmatized_root: true root from lemmatizer (e.g., "ajar")
        """
        if not word:
            return ('', '', '', '')
        
        original_word = word.lower()
        
        # Use pattern matching to get prefix, detected root, and suffix
        prefix, detected_root, suffix = self.analyze(original_word)
        
        # Use lemmatizer to get the accurate root word
        lemmatized_root = self.lemmatizer.lemmatize(original_word).strip()
        
        return (prefix, detected_root, suffix, lemmatized_root)
    
    def _reconstruct_morphemes(self, word, root):
        """
        Reconstruct prefix and suffix when root is not directly found in word.
        This handles cases like nasal assimilation (pe + m + baca → membaca).
        """
        # Use the original analyze method to get prefix/suffix boundaries
        prefix, _, suffix = self.analyze(word)
        
        # The root from lemmatizer is more accurate, use that
        # But we need to figure out what's between prefix and root
        
        # If we have a prefix, check if there's an infix between prefix and root
        if prefix:
            # Calculate what should be between prefix and suffix
            # word = prefix + ??? + suffix
            prefix_end = len(prefix)
            suffix_start = len(word) - len(suffix) if suffix else len(word)
            middle_part = word[prefix_end:suffix_start]
            
            # The middle part should contain the root, possibly with modifications
            # For now, keep the detected prefix and suffix
            return (prefix, root, suffix)
        
        # No prefix detected, check for suffix only
        if suffix:
            # word = root + suffix, but root might be modified
            return ('', root, suffix)
        
        # No affixes detected
        return ('', root, '')

if __name__ == '__main__':
    # Test the analyzer
    analyzer = MorphologicalAnalyzer()
    
    test_words = [
        'pembelajaran',
        'membaca',
        'berjalan',
        'kebersamaan',
        'diperjualbelikan',
        'Indonesia'
    ]
    
    for word in test_words:
        prefix, root, suffix = analyzer.analyze(word)
        print(f"{word:20} → prefix: '{prefix}', root: '{root}', suffix: '{suffix}'")
