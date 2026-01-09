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
            
            # If no infix found in prefix, check if root starts with a potential infix
            # This handles cases like "pembelajaran" where prefix="pe", root="mbelajar"
            # The "m" should be extracted as an infix
            if not infix and prefix in ['pe', 'be', 'me', 'te', 'se'] and root:
                # Check if root starts with a potential infix
                potential_infixes = ['ng', 'ny', 'm', 'n', 'l', 'r']
                for potential_infix in potential_infixes:
                    if root.startswith(potential_infix):
                        # Extract the infix from the root
                        infix = potential_infix
                        root = root[len(potential_infix):]  # Remove infix from root
                        base_prefix = prefix
                        break
            
            print(f"DEBUG: word='{word}', prefix='{prefix}', base='{base_prefix}', infix='{infix}', root='{root}'")
            
            if infix:
                # We have a prefix with infix (e.g., "pem" = "pe" + "m")
                # Split them into separate syllables
                result.append(base_prefix)
                result.append(infix)
            else:
                # No infix, just add the prefix as-is
                result.append(prefix)
        
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
