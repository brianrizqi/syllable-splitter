# Morphological Analyzer for Indonesian Language
# Detects prefixes, suffixes, and circumfixes

from nlp_id.lemmatizer import Lemmatizer

class MorphologicalAnalyzer:
    
    def __init__(self):
        # Initialize lemmatizer for accurate root detection
        self.lemmatizer = Lemmatizer()
        
        # Indonesian prefixes (sorted by length for greedy matching)
        self.prefixes = [
            'memper', 'mempel', 'pember', 'pembel', 'penyer', 'penyel', 'diper', 'dipel',
            'me', 'mem', 'men', 'meny', 'meng', 'pen', 'pem', 'peng', 'pe', 'ber', 'ter', 'di', 'ke', 'se', 'per', 'be', 'pel', 'te'
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
        
        # Internal infixes (TBBBI 4.3.1.6)
        self.internal_infixes = ['el', 'er', 'em', 'in']
        
        # Circumfixes (prefix + suffix combinations)
        self.circumfixes = [
            # memper- / diper- (longest/most specific first)
            ('memper', 'kan'), ('memper', 'i'), ('mempel', 'i'),
            ('diper', 'kan'), ('diper', 'i'), ('dipel', 'i'),
            ('pembel', 'an'), ('pember', 'an'),
            ('penyel', 'an'), ('penyer', 'an'),
            # per- (prioritize -kan/-i over -an)
            ('per', 'kan'), ('per', 'i'), ('per', 'an'),
            # ber- (prioritize -kan over -an)
            ('ber', 'kan'), ('ber', 'an'),
            # ke- + -an (nominalization)
            ('ke', 'an'),
            # pe- (nominalization/causative)
            ('pe', 'kan'), ('pe', 'i'), ('pe', 'an'),
            ('pem', 'kan'), ('pem', 'i'), ('pem', 'an'),
            ('pen', 'kan'), ('pen', 'i'), ('pen', 'an'),
            ('peng', 'kan'), ('peng', 'i'), ('peng', 'an'),
            ('peny', 'kan'), ('peny', 'i'), ('peny', 'an'),
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
        
        Indonesian prefixes can have infixes (peluluhan) inserted:
        - "per", "pen", "pem", "pel", "peng", "peny" → base "pe" + infix "r", "n", "m", "l", "ng", "ny"
        - "ber", "bel", "bem" → base "be" + infix "r", "l", "m"
        - "mer", "men", "mem", "mel", "meng", "meny" → base "me" + infix "r", "n", "m", "l", "ng", "ny"
        - "ter", "tel", "tem", "teng", "teny" → base "te" + infix "r", "l", "m", "ng", "ny"
        - "ser", "sel", "sem" → base "se" + infix "r", "l", "m"
        
        Args:
            prefix: The prefix string to decompose
            
        Returns:
            tuple: (base_prefix, infix) where infix is empty string if no infix detected
        """
        if not prefix:
            return ('', '')
        
        # Define base prefixes that can have infixes
        # Note: 'di' is not included because it doesn't have infix variations
        base_prefixes = ['pe', 'be', 'me', 'te', 'se']
        # Common infixes inserted after base prefixes (ordered by length for proper matching)
        infixes = ['ng', 'ny', 'm', 'l', 'r', 'n']
        
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
    
    def analyze_internal_infix(self, word):
        """
        Detect internal infixes (-el-, -er-, -em-, -in-) in base words.
        Example: "gerigi" -> infix="er", root="gigi"
        
        Returns:
            tuple: (internal_infix, root) or (None, word)
        """
        if len(word) < 5:  # Minimum length for C1 + Infix + C2 + V + C3 (e.g. g + er + igi)
            return (None, word)
            
        vowels = 'aiueo'
        # Regular consonants mapping for root reconstruction if needed
        # (Though usually it's just C1 + rest)
        
        # Forbidden prefix-like starts to avoid false infix detection
        # e.g. "per..." should be seen as prefix "per", not "p" + infix "er"
        forbidden_infix_starts = ['per', 'ber', 'ter', 'mem', 'pem', 'men', 'pen', 'meng', 'peng']
        
        for infix in self.internal_infixes:
            # Infix is usually at position 1 (after first consonant)
            # Pattern: C + Infix + RootRemainder
            if word[1:1+len(infix)] == infix and word[0] not in vowels:
                # Check if this start is actually a standard prefix
                prefix_check = word[0:1+len(infix)].lower()
                if prefix_check in forbidden_infix_starts:
                     # special case for "mem" and "pem" - they might be prefix + nasal
                     # but "gemetar" is "g" + "em". 
                     # we skip only if it's a very clear prefix start followed by a vowel
                     # actually, let's just avoid 'per', 'ber', 'ter' for now
                     if prefix_check in ['per', 'ber', 'ter']:
                          continue
                
                # Potential root is C1 + RootRemainder
                # e.g. "gerigi" -> g + igi = "gigi"
                potential_root = word[0] + word[1+len(infix):]
                
                # Validation: the potential root must have a valid syllable structure.
                # Specifically, after C1, the next character must be a vowel (CV pattern).
                # This prevents false positives like "kerja" -> "kja" (invalid).
                # True infixed words: "gerigi" -> "gigi" (g+i = valid CV).
                if len(potential_root) >= 2 and potential_root[1] not in vowels:
                    continue
                
                # Check if potential root "looks" like a valid word part (vowel present)
                if any(v in potential_root for v in vowels):
                    return (infix, potential_root)
                    
        return (None, word)

    def analyze_with_lemmatizer(self, word):
        """
        Analyze word using nlp-id lemmatizer for accurate root detection.
        Uses pattern matching for prefix/suffix boundaries.
        
        Returns:
            tuple: (prefix, detected_root, suffix, lemmatized_root, internal_infix)
        """
        if not word:
            return ('', '', '', '', None)
        
        original_word = word.lower()
        
        # Use pattern matching to get prefix, detected root, and suffix
        prefix, detected_root, suffix = self.analyze(original_word)
        
        # Use lemmatizer to get the accurate root word
        lemmatized_root = self.lemmatizer.lemmatize(original_word).strip()
        
        # Internal infix detection (TBBBI 4.3.1.6)
        internal_infix = None
        
        # Decision logic:
        # 1. If we have a clear prefix, trust it but check for infix in the root
        if prefix:
             # Logic for prefixed words that have infixed roots (e.g. "beterbangan")
             internal_infix, root_after_infix = self.analyze_internal_infix(detected_root)
             if internal_infix:
                  lemmatized_root = root_after_infix
        # 2. If no prefix detected, OR if prefix is suspect (lemmatizer doesn't agree)
        # Check for internal infix in the whole word
        else:
             internal_infix, root_after_infix = self.analyze_internal_infix(original_word)
             if internal_infix:
                  lemmatized_root = root_after_infix
        
        # 3. Special case for Suspect Prefix (e.g. "selidik" -> prefix "se" but root is "sidik")
        # If we didn't find an infix yet, but lemmatizer says the word is a base word, 
        # and we saw a prefix, try re-analyzing as a base word with infix.
        if not internal_infix and prefix and lemmatized_root == original_word:
             internal_infix, root_after_infix = self.analyze_internal_infix(original_word)
             if internal_infix:
                  lemmatized_root = root_after_infix
                  prefix = '' # It's actually a base word with an infix
                  detected_root = original_word
        
        return (prefix, detected_root, suffix, lemmatized_root, internal_infix)
    
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
