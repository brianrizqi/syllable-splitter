# Official PUEBI Syllable Splitter
# Based on rules from https://ivanlanin.github.io/puebi/kata/pemenggalan-kata/
# 
# PUEBI Rules for Pemenggalan Kata (Word Hyphenation):
# 1. VV (non-diphthong) → V-V (bu-ah, ma-in)
# 2. Diphthongs (ai, au, ei, oi) → not split (pan-dai, sau-da-ra)
# 3. VCV → V-CV (ba-pak, la-wan)
# 4. VCCV → VC-CV (man-di, som-bong) - split between consonants
# 5. VCCCV → VC-CCV (in-stru-men, ul-tra)
# 6. Consonant clusters (ng, ny, sy, kh, etc.) → not split (ba-nyak, makh-luk)
# 7. Kata berimbuhan → split at morpheme boundaries (ber-jalan, makan-an)

class PUEBIOfficialSplitter:
    
    def __init__(self):
        # Vokal (vowels)
        self.vowels = set('aiueo')
        
        # Diftong (diphthongs) - tidak dipenggal
        self.diphthongs = ['ai', 'au', 'ei', 'oi']
        
        # Gabungan huruf konsonan yang melambangkan satu bunyi - tidak dipenggal
        self.consonant_clusters = ['ng', 'ny', 'sy', 'kh', 'ch', 'dh', 'gh', 'ph', 'sh', 'th']
    
    def is_vowel(self, char):
        """Check if character is a vowel"""
        return char.lower() in self.vowels
    
    def split_syllables(self, word):
        """
        Split word into syllables following official PUEBI rules
        """
        if not word:
            return []
        
        word = word.lower()
        syllables = []
        i = 0
        current = ""
        
        while i < len(word):
            current += word[i]
            
            # Look ahead to decide where to split
            if i < len(word) - 1:
                # Rule 1 & 2: Check for vowel-vowel pattern
                if self.is_vowel(word[i]) and self.is_vowel(word[i+1]):
                    # Check if it's a diphthong
                    two_chars = word[i:i+2]
                    if two_chars not in self.diphthongs:
                        # VV (non-diphthong) → V-V
                        syllables.append(current)
                        current = ""
                        i += 1
                        continue
                
                # Rules 3, 4, 5: Analyze consonant patterns after vowel
                if self.is_vowel(word[i]):
                    # Count consecutive consonants ahead
                    j = i + 1
                    consonants = ""
                    while j < len(word) and not self.is_vowel(word[j]):
                        consonants += word[j]
                        j += 1
                    
                    # Check if there's a vowel after the consonants
                    has_vowel_after = j < len(word)
                    
                    if has_vowel_after and len(consonants) > 0:
                        if len(consonants) == 1:
                            # Rule 3: VCV → V-CV
                            syllables.append(current)
                            current = ""
                        elif len(consonants) >= 2:
                            # Check for consonant cluster (Rule 6)
                            first_two = consonants[:2]
                            if first_two in self.consonant_clusters:
                                # Cluster stays together: V-CCV
                                syllables.append(current)
                                current = ""
                            else:
                                # Rule 4 & 5: VCCV → VC-CV or VCCCV → VC-CCV
                                # Split after first consonant
                                current += consonants[0]
                                syllables.append(current)
                                current = ""
                                i += 1  # Skip the consonant we just added
            
            i += 1
        
        # Add remaining characters
        if current:
            syllables.append(current)
        
        return syllables

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Split string into syllables following official PUEBI rules.")
    parser.add_argument("string", help="string to be splitted.")
    
    args = parser.parse_args()
    
    splitter = PUEBIOfficialSplitter()
    syllables = splitter.split_syllables(args.string)
    
    print(f"Result: {syllables}")
    print(f"Joined: {'-'.join(syllables)}")
