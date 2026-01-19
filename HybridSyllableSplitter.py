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
            
            # Special handling for prefixes like 'penge', 'peny', 'ber', etc.
            # that contain an infix but weren't decomposed (e.g., 'penge' → 'pe' + 'ng' + 'e')
            if not infix and len(prefix) >= 4:
                vowels = 'aiueo'
                two_char_infixes = ['ng', 'ny']
                base_prefixes = ['pe', 'be', 'me', 'te', 'se']
                
                # Check if prefix matches pattern: base_prefix + two_char_infix + vowel
                # Example: 'penge' = 'pe' + 'ng' + 'e'
                for base in base_prefixes:
                    for infix_pattern in two_char_infixes:
                        if (prefix.startswith(base + infix_pattern) and 
                            len(prefix) > len(base + infix_pattern) and
                            prefix[len(base + infix_pattern)] in vowels):
                            # Extract the infix and prepend the vowel to the root
                            base_prefix = base
                            infix = infix_pattern
                            vowel_part = prefix[len(base + infix_pattern):]
                            root = vowel_part + root if root else vowel_part
                            break
                    if infix:
                        break
            
            # CRITICAL: Check if we should restore consonants for nasal assimilation
            # This handles cases where original consonant was assimilated during prefix attachment
            # Example: "memisah" → detected_root="isah", should restore "p" to get "pisah"
            #          "mengetik" → detected_root="etik", should restore "k" to get "ketik"
            # BUT NOT: "mengemban" → detected_root="emb", lemmatized_root="emban" (no restoration needed)
            if infix and root and len(root) > 0:
                vowels = 'aiueo'
                
                # If detected root starts with vowel, check if we need to restore consonant
                if root[0] in vowels:
                    # Strip suffix from lemmatized_root to get pure root
                    pure_lemmatized_root = lemmatized_root
                    if suffix and lemmatized_root and lemmatized_root.endswith(suffix):
                        pure_lemmatized_root = lemmatized_root[:-len(suffix)]
                    
                    # PRIORITY 1: Check if pure lemmatized root also starts with vowel
                    # If yes, no peluluhan occurred - use FULL lemmatized root
                    # Example: "mengemban" → detected_root="emb", lemmatized_root="emban"
                    # The morphological analyzer incorrectly split "emban" into "emb"+"an"
                    # We should use the full "emban" from lemmatizer and clear the suffix
                    if pure_lemmatized_root and pure_lemmatized_root[0] in vowels:
                        # No peluluhan - root naturally starts with vowel
                        # Use FULL lemmatized root (including what was detected as suffix)
                        root = lemmatized_root
                        suffix = ''  # Clear suffix since it's part of the root
                        # Don't clear infix - we still want to separate it
                    # PRIORITY 2: Restore based on infix type (most reliable for peluluhan)
                    # ng → k, ny → s, m → p, n → t
                    # This handles cases where lemmatizer returns incomplete root
                    # Example: "mengetik" → detected_root="etik", restore 'k' to get "ketik"
                    else:
                        consonant_map = {
                            'ng': 'k',
                            'ny': 's', 
                            'm': 'p',
                            'n': 't'
                        }
                        
                        if infix in consonant_map:
                            # Restore the consonant based on infix mapping
                            restored_consonant = consonant_map[infix]
                            root = restored_consonant + root
                            # Don't clear infix - we still want to separate it
                        elif pure_lemmatized_root and pure_lemmatized_root[0] not in vowels:
                            # PRIORITY 3: Use pure lemmatized root if available and starts with consonant
                            # This handles cases where lemmatizer correctly returns the root
                            root = pure_lemmatized_root
                            # Don't clear infix
                        else:
                            # PRIORITY 4: Regular peluluhan case - infix becomes part of root
                            # This is for cases where the infix is truly part of the root
                            root = infix + root
                            infix = ''
            
            # If no infix found in prefix, check if root starts with a potential infix
            # This handles cases like "pembelajaran" where prefix="pe", root="mbelajar"
            # The "m" should be extracted as an infix ONLY if it forms a consonant cluster
            if not infix and prefix in ['pe', 'be', 'me', 'te', 'se'] and root:
                # FIRST: Check if detected_root has a leading consonant that's not in lemmatized_root
                # Example: "perubahan" → detected_root="rubah", lemmatized_root="ubah"
                # The 'r' should be extracted as infix
                # IMPORTANT: Handle both single and two-character infixes
                # NOT for nested prefixes like "pembelajaran" where detected_root="mbelajar", lemmatized_root="ajar"
                vowels = 'aiueo'
                potential_infixes = ['m', 'n', 'l', 'r']
                two_char_infixes = ['ng', 'ny']
                
                if lemmatized_root and len(root) >= 2:
                    # Check for two-character infixes first (ng, ny)
                    # Example: "pengecualian" → detected_root="ngecuali", lemmatized_root="kecuali"
                    # The 'ng' should be extracted, even though length diff is 1 (ng replaces k)
                    if (len(root) >= 2 and 
                        root[:2] in two_char_infixes and
                        not lemmatized_root.startswith(root[:2])):
                        # Extract the two-character infix
                        # Example: "pengecualian" → extract 'ng', use "kecuali"
                        infix = root[:2]
                        root = lemmatized_root
                        # Only clear suffix if lemmatized_root includes it
                        if suffix and lemmatized_root.endswith(suffix):
                            suffix = ''  # Clear suffix since it's part of the root
                        base_prefix = prefix
                    # Check for single-character infixes
                    # Only if length difference is exactly 1 (to avoid nested prefixes)
                    elif (len(root) - len(lemmatized_root) == 1 and
                        root[0] in potential_infixes and
                        root[0] not in vowels):
                        # Check if lemmatized_root starts with a different character
                        # This indicates the first character is an infix
                        if (lemmatized_root[0] in vowels or 
                            (lemmatized_root[0] not in vowels and lemmatized_root[0] != root[0])):
                            # Extract the first character as infix
                            # Example: "perubahan" → extract 'r', use "ubah"
                            infix = root[0]
                            root = lemmatized_root
                            # Only clear suffix if lemmatized_root includes it
                            # Example: "mengemban" → lemmatized_root="emban" includes "an", clear it
                            # But "perubahan" → lemmatized_root="ubah" doesn't include "an", keep it
                            if suffix and lemmatized_root.endswith(suffix):
                                suffix = ''  # Clear suffix since it's part of the root
                            base_prefix = prefix
                # SECOND: Check if this is a nasal assimilation case using lemmatized root
                # Example: "memakai" → prefix="me", detected_root="maka", lemmatized_root="pakai"
                # Example: "penurunan" → prefix="pe", detected_root="nurun", lemmatized_root="turun"
                # We want to extract "m" or "n" as infix and use the lemmatized root
                if (not infix and 
                    lemmatized_root and 
                    len(root) >= 2 and 
                    root[0] in potential_infixes and 
                    root[1] in vowels):
                    assimilated_consonants = 'ptks'
                    if lemmatized_root[0] in assimilated_consonants:
                        # This is nasal assimilation: extract infix and use lemmatized root
                        # Example: "memakai" → detected_root="maka", lemmatized_root="pakai"
                        # The morphological analyzer incorrectly split "pakai" into "maka"+"i"
                        infix = root[0]
                        root = lemmatized_root
                        # Only clear suffix if lemmatized_root includes it
                        # Example: "memakai" → lemmatized_root="pakai" includes "i", clear it
                        # But "penurunan" → lemmatized_root="turun" doesn't include "an", keep it
                        if suffix and lemmatized_root.endswith(suffix):
                            suffix = ''  # Clear suffix since it's part of the root
                        base_prefix = prefix
                else:
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
                        
                        # Only extract as infix if first char is consonant AND second char is also consonant
                        # This means it's a consonant cluster that needs splitting
                        if first_char not in vowels and second_char not in vowels:
                            # It's a consonant cluster, extract first consonant as infix
                            if first_char in potential_infixes:
                                infix = first_char
                                root = root[1:]  # Remove infix from root
                                base_prefix = prefix
                        # If second char is a vowel, it's peluluhan - keep consonant with root
            

            
            if infix:
                # We have a prefix with infix (e.g., "pem" = "pe" + "m")
                # Split them into separate syllables
                result.append(base_prefix)
                result.append(infix)
            else:
                # No infix, just add the base prefix
                result.append(base_prefix)
            
            # NESTED PREFIX CHECK: After extracting first prefix+infix, check if root has another prefix
            # Example: "pembelajaran" → "pe" + "m" extracted, now check if "belajar" has "be" + "l"
            if root and len(root) > 2:
                # Check if root starts with a decomposable prefix
                nested_base_prefixes = ['pe', 'be', 'me', 'te', 'se']
                for nested_prefix in nested_base_prefixes:
                    if root.startswith(nested_prefix) and len(root) > len(nested_prefix):
                        # Check if there's an infix after this prefix
                        potential_infix_part = root[len(nested_prefix):]

                        if len(potential_infix_part) >= 2:
                            first_char = potential_infix_part[0]
                            second_char = potential_infix_part[1]
                            vowels = 'aiueo'
                            potential_infixes = ['m', 'n', 'l', 'r', 'ng', 'ny']
                            
                            # Check for two-char infixes first (ng, ny)
                            if potential_infix_part[:2] in ['ng', 'ny']:
                                nested_infix = potential_infix_part[:2]
                                remaining_root = potential_infix_part[2:]
                                if len(remaining_root) >= 2:  # Ensure remaining root is valid
                                    result.append(nested_prefix)
                                    result.append(nested_infix)
                                    root = remaining_root

                                    break
                            # Check for single-char infixes
                            # The infix can be followed by either consonant OR vowel
                            # Example: "belajar" → "be" + "l" + "ajar" (l followed by vowel a)
                            elif first_char in potential_infixes:
                                nested_infix = first_char
                                remaining_root = potential_infix_part[1:]
                                if len(remaining_root) >= 2:  # Ensure remaining root is valid
                                    result.append(nested_prefix)
                                    result.append(nested_infix)
                                    root = remaining_root

                                    break
        
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
