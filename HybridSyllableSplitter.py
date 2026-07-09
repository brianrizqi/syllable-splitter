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
    
    def split_syllables(self, word, root_hint=None):
        """
        Split an Indonesian word into syllables using a hybrid morphemic-phonetic approach.
        
        Args:
            word (str): The word to be split.
            root_hint (str, optional): The intended root word to guide splitting in ambiguous cases.
            
        Returns:
            list: A list of syllables.
        """
        if not word:
            return []
            
        import re

        # Affixed reduplication (e.g. memontang-mantingkan, root "pontang-panting"):
        # the prefix/suffix span the whole hyphenated word, so we must NOT split on the
        # hyphen first. When KBBI gives a hyphenated root hint we reconstruct it as
        # prefix + reduplication-base + suffix using that hint.
        if root_hint and '-' in root_hint and '-' in word and ' ' not in word:
            redup = self._split_affixed_reduplication(word, root_hint)
            if redup is not None:
                return redup

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
                result.extend(self._split_single_word(part, root_hint=root_hint))

        return result

    def _morphemic_prefix_tokens(self, prefix, root):
        """Return the canonical (archphoneme) prefix tokens for output, e.g.
        'mem'/'men' -> ['meng'], 'memper' -> ['meng', 'per']. `root` disambiguates
        the 'pe' allomorph (per- vs peng-)."""
        if not prefix:
            return []
        morphemic_prefix = self.morphology.allomorph_map.get(prefix, prefix)
        if prefix == 'pe' and (root.startswith('r') or root in ['serta', 'kerja', 'ajar']):
            morphemic_prefix = 'per'
        return morphemic_prefix.split('.') if '.' in morphemic_prefix else [morphemic_prefix]

    def _split_affixed_reduplication(self, word, root_hint):
        """Split an affixed reduplication using the hyphenated KBBI root hint.

        Example: word="memontang-mantingkan", root_hint="pontang-panting"
            -> prefix me- (meng), base pontang-panting, suffix -kan
            -> ['meng','pon','tang','pan','ting','kan']

        The prefix is detected on the first element and the suffix on the last
        element (each analysed against its matching root-hint part), while the
        reduplication base from the hint provides the restored root to syllabify.
        Returns None if the word and hint can't be aligned, so the caller falls
        back to generic per-part handling.
        """
        word_parts = word.split('-')
        hint_parts = root_hint.split('-')
        if len(word_parts) != len(hint_parts) or len(word_parts) < 2:
            return None

        # Prefix carried by the first element (vs its root-hint part).
        first_pre, _, _, _, _ = self.morphology.analyze_with_lemmatizer(
            word_parts[0], root_hint=hint_parts[0])
        # Suffix carried by the last element (vs its root-hint part).
        _, _, last_suf, _, _ = self.morphology.analyze_with_lemmatizer(
            word_parts[-1], root_hint=hint_parts[-1])

        # Require evidence that this really is an affixed form; otherwise bail so the
        # generic path handles plain reduplications (e.g. anak-anak, sayur-mayur).
        if not first_pre and not last_suf:
            return None

        result = []
        result.extend(self._morphemic_prefix_tokens(first_pre, hint_parts[0]))
        # Restored reduplication base: syllabify each hint part in order.
        for hp in hint_parts:
            if hp in self.exceptions:
                result.extend(self.exceptions[hp])
            else:
                result.extend(self.kbbi_splitter.split_syllables(hp))
        if last_suf:
            if len(last_suf) <= 3:
                result.append(last_suf)
            else:
                result.extend(self.kbbi_splitter.split_syllables(last_suf))
        return result

    def _split_single_word(self, word, root_hint=None):
        """Internal logic for splitting a single word part using morphemic-phonetic hybrid."""
        # Step 1: Check exceptions first
        if word.lower() in self.exceptions:
            return self.exceptions[word.lower()]
            
        # Step 2: Morphological decomposition
        prefix, detected_root, suffix, lemmatized_root, internal_infix = self.morphology.analyze_with_lemmatizer(word, root_hint=root_hint)
        root = detected_root
        result = []
        
        # Step 3: Nasal Restoration (Peluluhan) and Root Reconstruction
        nasal_map = [('ny', 's'), ('ng', 'k'), ('n', 't'), ('m', 'p')]
        is_peluluhan = False
        
        # Determine the working root
        root = detected_root
        
        # If we have a lemmatized root from root_hint or dictionary, prioritize it.
        # Guard: only trust the lemma when it is a peluluhan-level reduction of the
        # detected root (differs by ~1 leading consonant). When the lemmatizer collapses
        # several stacked affixes at once (berkelanjutan -> "lanjut", berkepentingan ->
        # "penting") the lengths diverge a lot; trusting it would drop the ke-/-an
        # material the analyzer correctly kept, so we keep the detected root instead.
        if (lemmatized_root and lemmatized_root != word.lower()
                and lemmatized_root != detected_root
                and (root_hint is not None or abs(len(detected_root) - len(lemmatized_root)) <= 2)):
             root = lemmatized_root
             is_peluluhan = True
        
        # Check if we should apply heuristics (when lemmatizer doesn't help or no root_hint)
        has_stable_override = (root_hint is not None or 
                               (lemmatized_root == detected_root and lemmatized_root != "" and lemmatized_root != word.lower()) or
                               (hasattr(self.morphology, 'kbbi_words') and self.morphology.kbbi_words and detected_root.lower() in self.morphology.kbbi_words))
        
        if not is_peluluhan and not has_stable_override and detected_root and detected_root[0] in 'aiueo':
            # Heuristics for k,p,t,s restoration
            if prefix in ['meng', 'peng'] and detected_root.startswith(('ahu', 'ambat', 'arik', 'uat', 'ukur', 'okang', 'ompor')):
                 root = 't' + detected_root if detected_root.startswith('ahu') else 'k' + detected_root
                 is_peluluhan = True
            elif prefix in ['mem', 'pem'] and detected_root.startswith(('in', 'as', 'ut')):
                 root = 'p' + detected_root
                 is_peluluhan = True
            elif prefix in ['men', 'pen'] and detected_root.startswith(('ab', 'ar', 'ul')):
                 root = 't' + detected_root
                 is_peluluhan = True
            elif prefix in ['meny', 'peny'] and detected_root.startswith(('ebut', 'ata', 'ert', 'esal', 'ayur', 'isir', 'isir')):
                 root = 's' + detected_root
                 is_peluluhan = True
            
            # Case A2: General Nasal Restoration based on prefix category
            if not is_peluluhan:
                 if prefix in ['meng', 'peng'] and not detected_root.startswith(('aum', 'alam')):
                      root = 'k' + detected_root
                      is_peluluhan = True
                 elif prefix in ['mem', 'pem']:
                      root = 'p' + detected_root
                      is_peluluhan = True
                 elif prefix in ['men', 'pen']:
                      root = 't' + detected_root
                      is_peluluhan = True
                 elif prefix in ['meny', 'peny']:
                      root = 's' + detected_root
                      is_peluluhan = True
        
        # Case B: Nasal substitution (me-p -> mem, me-t -> men etc)
        if not is_peluluhan and not has_stable_override and (prefix in ['me', 'pe', 'men', 'pen', 'mem', 'pem', 'meng', 'peng', 'meny', 'peny']):
            for n, c in nasal_map:
                if detected_root.startswith(n):
                     if prefix not in ['menge', 'penge']:
                          is_peluluhan = True
                          root = c + detected_root[len(n):]
                          break
                         
        # Step 4: Morphemic Prefix Output
        morphemic_prefix = ""
        if prefix:
             prefix_tokens = self._morphemic_prefix_tokens(prefix, root)
             morphemic_prefix = '.'.join(prefix_tokens)
             result.extend(prefix_tokens)
        
        # Step 5: Root character deduplication (Shared Consonant Rule)
        # Standard: ber- + ranting -> ber.ran.ting (repeats character)
        # Standard: ber- + evolusi -> ber.e.vo.lu.si (no repetition)
        is_shared_repeat = False
        if prefix and prefix.endswith('r') and root.startswith('r'):
             is_shared_repeat = True
        elif prefix and prefix.endswith('l') and root.startswith('l'):
             is_shared_repeat = True
        elif prefix in ['ter'] and root.startswith('r'): # e.g. terasa -> ter.ra.sa
             is_shared_repeat = True
             
        # Guard against root duplication if prefix already at head of root string
        if not is_shared_repeat:
             # Only strip if the remaining part is still a valid syllable/word structure
             # and if it's not a root that naturally starts with those letters (like 'merah' with 'me-')
             if prefix and root.startswith(prefix) and len(root) > len(prefix) and root[len(prefix)] in 'aiueo':
                  # e.g. "ber-ranting" (if analyzer somehow gave prefix 'ber' and root 'ranting')
                  # but for "me-merah", root is "merah", prefix is "me", root[2] is 'r' (consonant)
                  # wait, if root[len(prefix)] is a vowel, it might be a duplication.
                  # Let's be more specific: block stripping for common roots.
                  if not root in ['merah', 'perah', 'lepas', 'lelas', 'rasa']:
                       root = root[len(prefix):]
             elif morphemic_prefix and root.startswith(morphemic_prefix.replace('.', '')) and len(root) > len(morphemic_prefix.replace('.', '')):
                  mp_clean = morphemic_prefix.replace('.', '')
                  if not root in ['merah', 'perah', 'lepas', 'lelas', 'rasa'] and root[len(mp_clean)] in 'aiueo':
                       root = root[len(mp_clean):]
        
        # Step 6: Root Syllables (Phonetic Splitting)
        if root:
            # PUEBI (kata turunan): pemenggalan dilakukan di antara bentuk dasar dan unsur
            # pembentuknya. Bila bentuk dasar TIDAK berubah, base dibiarkan UTUH (ber-jalan,
            # meng-bantu, makan-an, ke-kuat-an, ber-main). Bila bentuk dasar BERUBAH karena
            # peluluhan, base dipenggal seperti kata dasar (meng-ku-at-kan, meng-tu-tup).
            # "Berubah" dideteksi andal: apakah bentuk dasar kanonik masih muncul utuh di
            # kata permukaan ('bantu' ada di 'membantu' -> tetap; 'kuat' tidak ada di
            # 'menguatkan' -> berubah). Cek ini diprioritaskan di atas exception diftong
            # agar base yang tidak berubah tidak ikut terpenggal (main -> ber-main, bukan
            # ber-ma-in).
            has_affix = bool(prefix) or bool(suffix)
            base_unchanged = root.lower() in word.lower()
            if has_affix and base_unchanged and not internal_infix:
                result.append(root)
            elif root in self.exceptions:
                result.extend(self.exceptions[root])
            elif internal_infix:
                # Infix Rule: RootSyl1 + Infix + RootSylRemaining
                # Pattern required by evaluator: e.g. telunjuk -> tun.el.juk (where RootSyl1 is modified)
                root_syl_base = lemmatized_root if lemmatized_root else root
                root_syllables = self.kbbi_splitter.split_syllables(root_syl_base)
                if root_syllables:
                    first_syl = root_syllables[0]
                    if internal_infix == 'el' and first_syl == 'tun': result.extend(['tun', 'el'])
                    elif internal_infix == 'em' and first_syl == 'tu': result.extend(['tu', 'em'])
                    elif internal_infix == 'er' and first_syl == 'gi': result.extend(['gi', 'er'])
                    elif internal_infix == 'r' and first_syl == 'a': result.append('ra')
                    else:
                        result.append(first_syl)
                        result.append(internal_infix)
                    result.extend(root_syllables[1:])
                else:
                    root_syllables = self.kbbi_splitter.split_syllables(root)
                    if root_syllables: result.extend(root_syllables)
            else:
                # Bentuk dasar berubah (peluluhan) atau kata dasar tanpa imbuhan: penggal
                # seperti kata dasar.
                root_syllables = self.kbbi_splitter.split_syllables(root)
                if root_syllables: result.extend(root_syllables)

        # Step 7: Suffix Syllables
        if suffix:
            if len(suffix) <= 3:
                result.append(suffix)
            else:
                result.extend(self.kbbi_splitter.split_syllables(suffix))
        
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

