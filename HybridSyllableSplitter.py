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
        Main entry point for syllable splitting.
        Handles multi-word phrases and hyphens by tokenizing first.
        """
        if not word:
            return []
            
        import re
        # Tokenize by space and hyphen, preserving the delimiters
        parts = re.split(r'([ \-])', word)
        
        result = []
        for part in parts:
            if not part:
                continue
            if part == ' ':
                result.append(' ')
            elif part == '-':
                # Hyphens are treated as potential syllable boundaries, 
                # we skip them to avoid double/triple hyphens in joined output
                continue
            else:
                # Process the individual word/morpheme
                result.extend(self._split_single_word(part))
                
        return result

    def _split_single_word(self, word):
        """Internal logic for splitting a single word part."""
        # Step 1: Check exceptions first
        if word.lower() in self.exceptions:
            return self.exceptions[word.lower()]
            
        # Step 2: Morphological decomposition
        prefix, detected_root, suffix, lemmatized_root, internal_infix = self.morphology.analyze_with_lemmatizer(word)
        root = detected_root
        
        result = []

        # Step 2.5: High Priority Infix Splitting (TBBBI 4.3.1.6)
        # Pattern: RootSyl1 + Infix + RootRemaining
        # e.g. selenggara (root: senggara -> seng-ga-ra) -> seng-el-ga-ra
        #      kinerja   (root: kerja   -> ker-ja)     -> ker-in-ja
        #      gerigi    (root: gigi    -> gi-gi)      -> gi-er-gi
        # ONLY for base words (no prefix). Prefixed words are handled in Step 4.
        if internal_infix and not prefix:
            root_syllables = self.kbbi_splitter.split_syllables(lemmatized_root)
            if root_syllables:
                result.append(root_syllables[0])
                result.append(internal_infix)
                result.extend(root_syllables[1:])
                return result
        
        # Step 3: Handle prefix - ALWAYS decompose to check for infix
        if prefix:
            is_composite = False
            base_prefix, infix, full_prefix = '', '', ''
            is_modified, is_peluluhan = False, False
            
            # COMPOSITE PREFIX HANDLING (e.g. 'memper', 'pembel')
            composite_prefix_map = {
                'memper': ['me', 'per'],
                'mempel': ['me', 'per'],
                'pember': ['pe', 'ber'],
                'pembel': ['per', 'ber'], # Changed from ['pe', 'ber'] to ['per', 'ber']
                'diper': ['di', 'per'],
                'dipel': ['di', 'per'],
                'diber': ['di', 'ber'], # Added
                'keber': ['ke', 'ber'], # Added
                'keter': ['ke', 'ter']  # Added
            }
            
            if prefix in composite_prefix_map:
                result.extend(composite_prefix_map[prefix])
                # SPECIAL: If root starts with 'mpe' or 'mbe' (e.g. 'mempelajar'),
                # and lemmatized_root is 'ajar', it means the analyzer included
                # part of the prefix in the root. we strip it.
                if lemmatized_root == 'ajar' and (root.startswith('mpe') or root.startswith('mbe') or root.startswith('pel') or root.startswith('bel')):
                     root = lemmatized_root
                is_composite = True
                is_modified = False
            
            if not is_composite:
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
            
            # CRITICAL: RESTORE dropped 'r' or 'l' for be-/pel-/te- variants
            # These don't always count as 'modified' by simple comparison
            if base_prefix in ['be', 'pe', 'te']:
                 if lemmatized_root == 'ajar':
                      infix = 'r' # Always 'r' even if 'l' was detected
                 elif not infix:
                      if (lemmatized_root.startswith('r') or 
                          (len(lemmatized_root) > 2 and lemmatized_root[1:3] == 'er' and not self.kbbi_splitter.is_vowel(lemmatized_root[0])) or
                          (base_prefix == 'te' and lemmatized_root == 'pergok')):
                         infix = 'r'

            # CRITICAL: Check if we should restore consonants for nasal assimilation
            # This handles cases where original consonant was assimilated during prefix attachment
            if infix and root and len(root) > 0:
                vowels = 'aiueo'
                
                # If detected root starts with vowel, check if we need to restore consonant
                if root[0] in vowels:
                    # Strip suffix from lemmatized_root to get pure root
                    pure_lemmatized_root = lemmatized_root
                    if suffix and lemmatized_root and lemmatized_root.endswith(suffix):
                        pure_lemmatized_root = lemmatized_root[:-len(suffix)]
                    
                    # PRIORITY 1: Check if pure lemmatized root also starts with vowel
                    if pure_lemmatized_root and pure_lemmatized_root[0] in vowels:
                        # No peluluhan - root naturally starts with vowel
                        root = lemmatized_root
                        if suffix and lemmatized_root.endswith(suffix):
                             suffix = '' 
                        # Rule 1: Nasal is already part of the prefix, don't clear it
                    else:
                        # PRIORITY 2: Regular peluluhan case
                        # For be-/pe- (ber-/per-) variants, we preserve the infix to trigger
                        # the morphemic restoration later (e.g., ber-ram-but).
                        # For others (e.g. me-), we merge for phonetic processing.
                        if not (base_prefix in ['be', 'pe'] and infix in ['r', 'l']):
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
            

            
            # If we extracted an infix but didn't actually merge it into the root
            # (which means Rule 1 applies: base word intact), we need to reconstruct 
            # the full phonological prefix before splitting it.
            # E.g. base_prefix='me', infix='m' -> full_prefix='mem' 
            full_prefix = base_prefix
            if infix:
                full_prefix += infix
                
            # Reconstruct the pure lemmatized_root string based on suffix presence
            pure_root = lemmatized_root
            # Root-Priority Logic: Check if the stem is modified (peluluhan)
            # We compare the 'original_stem' (morphology output) with 'concatenated_stem' (lemmatizer + reconstructed prefix)
            original_stem = prefix + detected_root
            concatenated_stem = full_prefix + lemmatized_root
            
            
            # If the reconstructed stem matches the original start of the word exactly, it's Rule 1 (Root Intact)
            if not is_composite and original_stem == concatenated_stem:
                is_modified = False
                # Recalculate root and suffix to handle potential overlaps (e.g. berdesakan)
                root = lemmatized_root
                # suffix is everything after full_prefix + lemmatized_root
                suffix = word[len(full_prefix) + len(lemmatized_root):]
            elif not is_composite and word.startswith(concatenated_stem):
                # This covers cases like 'mengemban' or 'menilai' where the analyzer falsely truncated the root
                is_modified = False
                root = lemmatized_root
                suffix = word[len(full_prefix) + len(lemmatized_root):]
                is_modified = True
            
            # Special case for memper/diper: preserve prefix boundary
            if is_modified and prefix in ['memper', 'diper']:
                if detected_root + suffix == lemmatized_root:
                    is_modified = False
                    root = lemmatized_root
                    suffix = '' 
            
            if is_modified:
                # 1. Detect standard peluluhan (k, t, s, p)
                is_peluluhan = False
                nasal_part = ""
                
                # Check mapping of nasals to consonants
                nasal_map = [('ng', 'k'), ('ny', 's'), ('n', 't'), ('m', 'p')]
                
                # Case A: Short prefix (me-) + nasal-starting detected_root (ngerja)
                if prefix in ['me', 'pe', 'be', 'te', 'se']:
                    for n, c in nasal_map:
                        if detected_root.startswith(n) and lemmatized_root.startswith(c):
                            is_peluluhan = True
                            nasal_part = n
                            break
                            
                # Case B: Nasal-ending prefix (meng-) + vowel-starting detected_root (eluh)
                if not is_peluluhan:
                    for n, c in nasal_map:
                        if prefix.endswith(n) and lemmatized_root.startswith(c):
                            is_peluluhan = True
                            # Nasal is already in the prefix
                            break
                            
                # Case C: be-/pe-/te- variations (ber-/per-/ter-)
                if not is_peluluhan and base_prefix in ['be', 'pe', 'te']:
                    # be- + r... -> be... (e.g. berambut)
                    # be- + ...er... -> be... (e.g. bekerja)
                    if (lemmatized_root.startswith('r') or 
                        (len(lemmatized_root) > 2 and lemmatized_root[1:3] == 'er' and not self.kbbi_splitter.is_vowel(lemmatized_root[0]))):
                        is_peluluhan = True
                        nasal_part = 'r'
                    # bel- + ajar -> belajar (restored as ber-a-jar)
                    elif lemmatized_root == 'ajar' and prefix in ['be', 'pe', 'bel', 'pel']:
                        is_peluluhan = True
                        nasal_part = 'r'
                
                if is_peluluhan or base_prefix in ['pe', 'me', 'be', 'te']:
                    # MORPHEMIC PRIORITY: Restore original root boundary
                    # REFINED: Rule from User - all 'pe' variants (pe, pem, peng, pel) must be 'per'.
                    # For 'me', we still use 'me'.
                    if base_prefix == 'pe':
                        morphemic_prefix = 'per'
                    elif base_prefix == 'me':
                        morphemic_prefix = 'me'
                    elif base_prefix == 'te':
                        morphemic_prefix = 'ter'
                    elif nasal_part in ['r', 'l']:
                        # Handles ber-/bel- etc.
                        morphemic_prefix = base_prefix + nasal_part
                    else:
                        morphemic_prefix = base_prefix
                        
                    prefix_syllables = self.kbbi_splitter.split_syllables(morphemic_prefix)
                    result.extend(prefix_syllables)
                    
                    root = lemmatized_root
                    # Prevent duplication if lemmatized_root already contains the prefix
                    # (e.g. nested prefixes like 'berpendidikan' where lemmatizer failed)
                    if root.startswith(morphemic_prefix):
                         root = root[len(morphemic_prefix):]
                    if suffix and root.endswith(suffix):
                         suffix = ''
                else:
                    # PHONETIC PRIORITY: For complex modifications
                    # splitting the whole word phonetically is most reliable.
                    stem_syllables = self.kbbi_splitter.split_syllables(word)
                    result.extend(stem_syllables)
                    # Clear root and suffix so Step 4/5 are skipped
                    root = ""
                    suffix = ""
            elif not is_composite:
                # Rule 1: Base word intact (e.g. 'mengambil')
                # REFINED (Supervisor's Rule): Universalize 'pe' to 'per'. Use 'me' for 'meng-'.
                morphemic_prefix = full_prefix
                if base_prefix == 'me' and infix and infix not in ['r', 'l']:
                     morphemic_prefix = 'me'
                elif base_prefix == 'pe':
                     morphemic_prefix = 'per'
                     
                prefix_syllables = self.kbbi_splitter.split_syllables(morphemic_prefix)
                result.extend(prefix_syllables)
        
        # Step 4: Root - apply syllable rules (if not already handled by phonetic split)
        if root:
            if root in self.exceptions:
                result.extend(self.exceptions[root])
            elif internal_infix:
                # Root Infix Splitting: RootSyl1 + Infix + RootRemaining
                # e.g. menggelembung -> me-[gem-el-bung] (root: gembung -> gem-bung)
                root_syllables = self.kbbi_splitter.split_syllables(lemmatized_root)
                if root_syllables:
                    result.append(root_syllables[0])
                    result.append(internal_infix)
                    result.extend(root_syllables[1:])
                else:
                    result.extend(self.kbbi_splitter.split_syllables(root))
            else:
                root_syllables = self.kbbi_splitter.split_syllables(root)
                result.extend(root_syllables)
        
        # Step 5: Suffix - usually keep as one syllable (if not already handled)
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
    from SpellChecker import IndonesianSpellChecker
    
    parser = argparse.ArgumentParser(description="Hybrid morphological-syllable splitter.")
    parser.add_argument("string", help="string to be splitted.")
    parser.add_argument("--verbose", action="store_true", help="Show morphological analysis")
    parser.add_argument("--no-spell-check", action="store_true", help="Skip spell checking")
    
    args = parser.parse_args()
    
    # Spell check first (unless disabled)
    if not args.no_spell_check:
        spell_checker = IndonesianSpellChecker()
        errors = spell_checker.check_text(args.string)
        
        if errors:
            print("\n⚠️  PERINGATAN DETEKSI KATA:")
            print("=" * 60)
            
            # Categorize errors
            typos = [e for e in errors if e.get('error_type') == 'typo']
            not_found = [e for e in errors if e.get('error_type') == 'not_found']
            non_indonesian = [e for e in errors if e.get('error_type') == 'non_indonesian']
            
            # Colors for terminal
            RED = '\033[91m'
            YELLOW = '\033[93m'
            BLUE = '\033[94m'
            RESET = '\033[0m'
            BOLD = '\033[1m'
            
            if non_indonesian:
                print(f"\n{BLUE}{BOLD}🔵 Bukan Bahasa Indonesia:{RESET}")
                for error in non_indonesian:
                    print(f"  • {BOLD}{error['word']}{RESET} - {error['reason']}")
            
            if typos:
                print(f"\n{RED}{BOLD}🔴 Kemungkinan Typo:{RESET}")
                for error in typos:
                    print(f"  • {BOLD}{error['word']}{RESET} - {error['reason']}")
                    if error.get('suggestions'):
                        print(f"    Saran: {', '.join(error['suggestions'])}")
            
            if not_found:
                print(f"\n{YELLOW}{BOLD}🟡 Tidak Ditemukan di KBBI:{RESET}")
                for error in not_found:
                    print(f"  • {BOLD}{error['word']}{RESET}")
                    if error.get('suggestions'):
                        print(f"    Saran: {', '.join(error['suggestions'])}")
            
            print("\n" + "=" * 60)
            response = input("Lanjutkan pemisahan suku kata? (y/n): ")
            if response.lower() != 'y':
                print("Dibatalkan.")
                exit(0)
            print()
    
    splitter = HybridSyllableSplitter()
    syllables = splitter.split_syllables(args.string)
    
    if args.verbose:
        prefix, root, suffix = splitter.morphology.analyze(args.string)
        print(f"Morphology: prefix='{prefix}', root='{root}', suffix='{suffix}'")
    
    print(f"Result: {syllables}")
    print(f"Joined: {'-'.join(syllables)}")

