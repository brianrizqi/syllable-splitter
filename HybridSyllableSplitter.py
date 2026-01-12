# Hybrid Morphological-Syllable Splitter
# Combines morphological analysis with syllable splitting

import json
import os
from MorphologicalAnalyzer import MorphologicalAnalyzer
from KBBISyllableSplitter import KBBISyllableSplitter

class HybridSyllableSplitter:
    
    def __init__(self):
        self.morphology = MorphologicalAnalyzer()
        self.kbbi_splitter = KBBISyllableSplitter()
        self.exceptions = self.load_exceptions()
    
    def load_exceptions(self):
        """Load exception dictionary from JSON file"""
        try:
            exceptions_path = os.path.join(os.path.dirname(__file__), 'exceptions.json')
            with open(exceptions_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def split_syllables(self, word):
        """
        Split word into syllables using hybrid approach:
        1. Check exceptions first
        2. Detect morphemes (prefix + root + suffix)
        3. Decompose prefix into base prefix + infix if applicable
        4. Apply syllable rules to each morpheme
        5. Combine results
        """
        if not word:
            return []
        
        word_lower = word.lower()
        
        # Step 1: Check exceptions
        if word_lower in self.exceptions:
            return self.exceptions[word_lower]
        
        # Step 2: Morphological analysis using lemmatizer
        # detected_root has infixes (e.g., "mbelajar"), lemmatized_root is pure (e.g., "ajar")
        prefix, detected_root, suffix, lemmatized_root = self.morphology.analyze_with_lemmatizer(word)
        
        # Use detected_root for syllable splitting (it has the infixes we need to extract)
        root = detected_root
        
        result = []
        
        # Step 3: Handle prefix - ALWAYS decompose to check for infix
        if prefix:
            # Decompose prefix to check for infix
            base_prefix, infix = self.morphology.decompose_prefix(prefix)
            
            # CRITICAL FIX: Check if the infix should actually be kept with the root
            # This happens when root starts with a vowel (peluluhan case)
            # Example: "memisah" → prefix="mem" decomposes to base="me" + infix="m"
            #          but root="isah" starts with vowel, so "m" should stay with root → "mi-sah"
            if infix and root and len(root) > 0:
                vowels = 'aiueo'
                # If root starts with a vowel, the infix is from peluluhan
                # Put it back with the root, don't separate it
                if root[0] in vowels:
                    root = infix + root  # Combine infix back with root
                    infix = ''  # Clear the infix
            
            # If no infix found in prefix, check if root starts with a potential infix
            # This handles cases like "pembelajaran" where prefix="pe", root="mbelajar"
            # The "m" should be extracted as an infix ONLY if it forms a consonant cluster
            if not infix and prefix in ['pe', 'be', 'me', 'te', 'se'] and root:
                # Check if root starts with a consonant cluster that needs splitting
                # Only extract infixes when they form clusters (e.g., "mb", "ng", "ny")
                # NOT single consonants from peluluhan (e.g., "m" in "memisah" from "pisah")
                
                # Check for consonant clusters first (these should be split)
                consonant_clusters = ['mb', 'ng', 'ny']
                cluster_found = False
                
                for cluster in consonant_clusters:
                    if root.startswith(cluster):
                        # Extract the first consonant as infix
                        infix = cluster[0] if cluster != 'ng' and cluster != 'ny' else cluster
                        root = root[len(infix):]  # Remove infix from root
                        base_prefix = prefix
                        cluster_found = True
                        break
                
                # If no cluster found, check if it's a single consonant followed by a vowel
                # In this case, it's likely peluluhan, so DON'T extract it as infix
                if not cluster_found and len(root) >= 2:
                    first_char = root[0]
                    second_char = root[1]
                    vowels = 'aiueo'
                    
                    # Only extract as infix if first char is consonant AND second char is also consonant
                    # This means it's a consonant cluster that needs splitting
                    if first_char not in vowels and second_char not in vowels:
                        # It's a consonant cluster, extract first consonant as infix
                        potential_infixes = ['m', 'n', 'l', 'r']
                        if first_char in potential_infixes:
                            infix = first_char
                            root = root[1:]  # Remove infix from root
                            base_prefix = prefix
                    # If second char is a vowel, it's peluluhan - keep consonant with root
            
            print(f"DEBUG: word='{word}', prefix='{prefix}', base='{base_prefix}', infix='{infix}', root='{root}'")
            
            if infix:
                # We have a prefix with infix (e.g., "pem" = "pe" + "m")
                # Split them into separate syllables
                result.append(base_prefix)
                result.append(infix)
            else:
                # No infix, just add the base prefix
                result.append(base_prefix)
        
        # Step 4: Root - apply syllable rules
        if root:
            # Check if root is in exceptions
            if root in self.exceptions:
                result.extend(self.exceptions[root])
            else:
                # Split root normally using KBBI syllable rules
                root_syllables = self.kbbi_splitter.split_syllables(root)
                result.extend(root_syllables)

        
        # Step 5: Suffix - usually keep as one syllable
        if suffix:
            if len(suffix) <= 3:
                result.append(suffix)
            else:
                suffix_syllables = self.kbbi_splitter.split_syllables(suffix)
                result.extend(suffix_syllables)
        
        # If no morphemes detected, just split the whole word
        if not result:
            result = self.kbbi_splitter.split_syllables(word)
        
        return result

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Hybrid morphological-syllable splitter.")
    parser.add_argument("string", help="string to be splitted.")
    parser.add_argument("--verbose", action="store_true", help="Show morphological analysis")
    
    args = parser.parse_args()
    
    splitter = HybridSyllableSplitter()
    syllables = splitter.split_syllables(args.string)
    
    if args.verbose:
        prefix, root, suffix = splitter.morphology.analyze(args.string)
        print(f"Morphology: prefix='{prefix}', root='{root}', suffix='{suffix}'")
    
    print(f"Result: {syllables}")
    print(f"Joined: {'-'.join(syllables)}")
