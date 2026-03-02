import os
import sys

# Add current directory to path so we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from MorphologicalAnalyzer import MorphologicalAnalyzer

class PUEBIOfficialSplitter:
    
    def __init__(self):
        # Vokal (vowels)
        self.vowels = set('aiueo')
        
        # Diftong (diphthongs) - tidak dipenggal (Rule 1b)
        self.diphthongs = ['ai', 'au', 'ei', 'oi']
        
        # Gabungan huruf konsonan yang melambangkan satu bunyi - tidak dipenggal (Rule 1 note)
        self.consonant_clusters = ['ng', 'ny', 'sy', 'kh', 'ch', 'dh', 'gh', 'ph', 'sh', 'th']
        
        # Prefixes that trigger Rule 3 (Unsur gabungan)
        self.combining_prefixes = ['bio', 'foto', 'intro', 'kilo', 'pasca', 'mikro', 'multi', 'sub', 'super', 'panca', 'dwi', 'eka', 'tri', 'catur']
        
        # Initialize Morphological Analyzer for Rule 2
        self.morphology = MorphologicalAnalyzer()
    
    def is_vowel(self, char):
        """Check if character is a vowel"""
        return char.lower() in self.vowels
    
    def get_units(self, word):
        """Group word into vowels, consonant clusters, and single consonants"""
        units = []
        i = 0
        while i < len(word):
            # Check for clusters (2 chars)
            if i < len(word) - 1:
                cluster = word[i:i+2].lower()
                if cluster in self.consonant_clusters:
                    units.append(word[i:i+2])
                    i += 2
                    continue
            
            # Individual chars
            units.append(word[i])
            i += 1
        return units

    def split_base_word(self, word):
        """
        PUEBI Rule 1: Pemenggalan kata pada kata dasar
        """
        if not word:
            return []
        
        units = self.get_units(word)
        syllables = []
        current_syllable = ""
        
        i = 0
        while i < len(units):
            unit = units[i]
            current_syllable += unit
            
            # Look ahead for vowel patterns
            if i < len(units) - 1:
                # Rule 1a & 1b: Vowel-Vowel
                if self.is_vowel(unit) and self.is_vowel(units[i+1]):
                    # Check for diphthong (Rule 1b)
                    diph = (unit + units[i+1]).lower()
                    if diph in self.diphthongs:
                        # HEURISTIC: ai, au, ei, oi are diphthongs ONLY IF 
                        # they are at the end of the word OR followed by a consonant+vowel (CV)
                        # Example: 'pandai' (end), 'aula' (au-la), 'saudara' (sau-da-ra)
                        # NOT 'main' (follows by end-of-word consonant)
                        
                        is_diphthong = False
                        if i + 1 == len(units) - 1: # V1V2 is end of word
                            is_diphthong = True
                        elif i + 2 < len(units) and not self.is_vowel(units[i+2]):
                            # Look ahead for next part
                            if i + 3 < len(units) and self.is_vowel(units[i+3]):
                                # V1V2-CV pattern -> Diphthong
                                is_diphthong = True
                                
                        if not is_diphthong:
                            # Rule 1a: Split sequential vowels that are not diphthongs
                            syllables.append(current_syllable)
                            current_syllable = ""
                    else:
                        # Rule 1a: VV (non-diphthong) → V-V
                        syllables.append(current_syllable)
                        current_syllable = ""
                
                # Rule 1c, 1d, 1e: Consonants between vowels
                elif self.is_vowel(unit):
                    # Count consonant units ahead until next vowel
                    j = i + 1
                    cons_units = []
                    while j < len(units) and not self.is_vowel(units[j]):
                        cons_units.append(units[j])
                        j += 1
                    
                    if j < len(units) and self.is_vowel(units[j]):
                        # We have pattern: V + [Cons Units] + V
                        if len(cons_units) == 1:
                            # Rule 1c: V-CV
                            syllables.append(current_syllable)
                            current_syllable = ""
                        elif len(cons_units) == 2:
                            # Rule 1d: VC-CV
                            current_syllable += cons_units[0]
                            syllables.append(current_syllable)
                            current_syllable = ""
                            i += 1  # Skip the unit we just added
                        elif len(cons_units) >= 3:
                            # Rule 1e: VC-CCV (first-second boundary)
                            current_syllable += cons_units[0]
                            syllables.append(current_syllable)
                            current_syllable = ""
                            i += 1  # Skip first unit
            
            i += 1
            
        if current_syllable:
            syllables.append(current_syllable)
            
        return syllables

    def apply_single_letter_filter(self, syllables):
        """
        PUEBI Catatan 3: Pemenggalan kata yang menyebabkan munculnya 
        satu huruf di awal atau akhir baris tidak dilakukan.
        (Note: Di-disable untuk keperluan analisis silabel murni)
        """
        return syllables

    def split_syllables(self, word):
        """
        Main function to split syllables following all PUEBI rules
        """
        if not word:
            return []
            
        word_lower = word.lower()
        
        # Rule 3: Unsur Gabungan
        # PUEBI says: "Tiap unsur gabungan itu dipenggal seperti pada kata dasar."
        for prefix in sorted(self.combining_prefixes, key=len, reverse=True):
            if word_lower.startswith(prefix) and len(word_lower) > len(prefix):
                part1 = word[:len(prefix)]
                part2 = word[len(prefix):]
                # Split boundary first, then syllables for each part according to Rules 1 & 3
                raw_split = self.split_base_word(part1) + self.split_base_word(part2)
                return self.apply_single_letter_filter(raw_split)

        # Analyze morphology
        m_prefix, m_root, m_suffix, lem_root, internal_infix = self.morphology.analyze_with_lemmatizer(word)
        
        # Determine if it's a base word (Rule 1) or derived word (Rule 2)
        if word_lower == lem_root or not lem_root:
            return self.apply_single_letter_filter(self.split_base_word(word))

        # Rule 2: Kata Turunan (Derived Words)
        # We need to decide if we use Rule 2 (morpheme boundary) or Note 1/2 (syllable splitting)
        
        # Note 2: Sisipan (Infiks) -> Syllable based
        # Sisipan: -el-, -er-, -em-, -in-
        is_sisipan = False
        for inf in ['el', 'er', 'em', 'in']:
            if word_lower.startswith(word_lower[0] + inf) and word_lower[1:1+len(inf)] == inf:
                if m_prefix not in ['per', 'ber', 'ter', 'me', 'pe', 'di', 'ke', 'se']:
                    is_sisipan = True
                    break
        
        # Note 1: Apitan atau Luluhan (Simulfiks) -> Syllable based
        # If nasalized (m-root != lem-root) or root part in word differs from lemma
        is_simulfix = False
        if lem_root and lem_root in word_lower:
            start_idx = word_lower.find(lem_root)
            actual_root_part = word_lower[start_idx : start_idx + len(lem_root)]
            if actual_root_part != lem_root:
                is_simulfix = True
        else:
            # Root not found as-is (e.g., 'menutup' root 'tutup') -> Luluhan/Simulfiks
            is_simulfix = True
            
        if is_simulfix or is_sisipan:
            # Rule 2 Note 1 & 2: Split like base word (phonetic)
            return self.apply_single_letter_filter(self.split_base_word(word))

        # Rule 2 Standard: "dilakukan di antara bentuk dasar dan unsur pembentuknya"
        # For unchanged bases, we split ONLY at morpheme boundaries.
        if lem_root in word_lower:
            start_idx = word_lower.find(lem_root)
            prefix_part = word[:start_idx]
            root_part = word[start_idx : start_idx + len(lem_root)]
            suffix_part = word[start_idx + len(lem_root):]
            
            result = []
            if prefix_part:
                # Handle prefixes phonetically to naturally split composite prefixes
                # e.g., 'memper' -> 'mem-per', 'diper' -> 'di-per', 'diber' -> 'di-ber'
                result.extend(self.split_base_word(prefix_part))
            
            if root_part:
                result.extend(self.split_base_word(root_part))
                
            if suffix_part:
                # Split suffixes that might have multiple syllables
                result.extend(self.split_base_word(suffix_part))
                
            return self.apply_single_letter_filter(result)

        # Fallback to Rule 1: Kata Dasar (Syllable Based)
        return self.apply_single_letter_filter(self.split_base_word(word))

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Split string into syllables following official PUEBI rules.")
    parser.add_argument("string", help="string to be splitted.")
    
    args = parser.parse_args()
    
    splitter = PUEBIOfficialSplitter()
    syllables = splitter.split_syllables(args.string)
    
    print(f"Result: {syllables}")
    print(f"Joined: {'-'.join(syllables)}")

