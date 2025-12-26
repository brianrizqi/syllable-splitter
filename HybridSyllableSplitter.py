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
        
        # Step 3: Handle prefix with infix decomposition
        if prefix:
            # Decompose prefix to check for infix
            base_prefix, infix = self.morphology.decompose_prefix(prefix)
            
            if infix:
                # We have a prefix with infix (e.g., "pem" = "pe" + "m")
                result.append(base_prefix)
                result.append(infix)
            else:
                # No infix, treat prefix normally
                if len(prefix) <= 3:
                    result.append(prefix)
                else:
                    prefix_syllables = self.kbbi_splitter.split_syllables(prefix)
                    result.extend(prefix_syllables)
        
        # Step 4: Root - apply syllable rules
        if root:
            # Check if root is in exceptions
            if root in self.exceptions:
                result.extend(self.exceptions[root])
            else:
                # Check if root starts with a nasal consonant that's actually part of prefix
                # (e.g., "mbelajar" → "m" + "belajar" when prefix is "pe")
                # Only extract TRUE nasal consonants (m, n, ng, ny), not liquids (l, r)
                extracted_infix = ''
                remaining_root = root
                
                if prefix in ['pe', 'be', 'me']:
                    # Check for leading nasal consonants (not liquids!)
                    nasal_consonants = ['ng', 'ny', 'm', 'n']
                    for nasal in nasal_consonants:
                        if root.startswith(nasal) and len(root) > len(nasal):
                            extracted_infix = nasal
                            remaining_root = root[len(nasal):]
                            break
                
                if extracted_infix:
                    # Add the extracted infix as a separate syllable
                    result.append(extracted_infix)
                    # Now split the remaining root
                    if remaining_root:
                        # Check if remaining root is in exceptions
                        if remaining_root in self.exceptions:
                            result.extend(self.exceptions[remaining_root])
                        else:
                            remaining_syllables = self.kbbi_splitter.split_syllables(remaining_root)
                            result.extend(remaining_syllables)
                else:
                    # No extracted infix, split root normally
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
