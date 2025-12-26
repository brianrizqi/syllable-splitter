# PUEBI-Compliant Syllable Splitter
# Based on Pedoman Umum Ejaan Bahasa Indonesia (PUEBI)
# Matching KBBI syllable splitting output

class PUEBISyllableSplitter:
    
    def __init__(self):
        # Vokal (vowels)
        self.vowels = set('aiueo')
        
        # Diftong (diphthongs) - tidak dipenggal
        self.diphthongs = ['ai', 'au', 'ei', 'oi']
        
        # Gabungan konsonan yang melambangkan satu bunyi - tidak dipenggal
        self.consonant_clusters = ['ng', 'ny', 'sy', 'kh', 'ch', 'dh', 'gh', 'ph', 'sh', 'th']
        
    def is_vowel(self, char):
        """Check if character is a vowel"""
        return char.lower() in self.vowels
    
    def split_syllables(self, word):
        """
        Split word into syllables following PUEBI/KBBI rules
        
        Key rules:
        1. VV (non-diphthong) → V-V
        2. VCV → V-CV  
        3. VCCV → VC-CV (split between consonants)
        4. Consonant clusters (ng, ny, etc.) stay together
        """
        if not word:
            return []
        
        word = word.lower()
        syllables = []
        i = 0
        current = ""
        
        while i < len(word):
            current += word[i]
            
            # Determine if we should split after current position
            if i < len(word) - 1:
                # Check for vowel-vowel pattern (non-diphthong)
                if self.is_vowel(word[i]) and self.is_vowel(word[i+1]):
                    if word[i:i+2] not in self.diphthongs:
                        syllables.append(current)
                        current = ""
                        i += 1
                        continue
                
                # Check for vowel followed by consonant(s) then vowel
                if self.is_vowel(word[i]):
                    # Count consonants ahead
                    j = i + 1
                    while j < len(word) and not self.is_vowel(word[j]):
                        j += 1
                    
                    consonant_count = j - i - 1
                    
                    # If there's a vowel after the consonants
                    if j < len(word) and consonant_count > 0:
                        if consonant_count == 1:
                            # VCV → V-CV
                            syllables.append(current)
                            current = ""
                        else:
                            # VCCV or more
                            # Check if next two consonants form a cluster
                            if i + 2 < len(word):
                                two_cons = word[i+1:i+3]
                                if two_cons in self.consonant_clusters:
                                    # V-CCV (keep cluster with next syllable)
                                    syllables.append(current)
                                    current = ""
                                else:
                                    # VC-CV (split between consonants)
                                    current += word[i+1]
                                    syllables.append(current)
                                    current = ""
                                    i += 1
                            else:
                                # Only one more consonant, add it
                                current += word[i+1]
                                syllables.append(current)
                                current = ""
                                i += 1
            
            i += 1
        
        # Add remaining
        if current:
            syllables.append(current)
        
        return syllables

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Split string into syllables following PUEBI/KBBI rules.")
    parser.add_argument("string", help="string to be splitted.")
    
    args = parser.parse_args()
    
    splitter = PUEBISyllableSplitter()
    syllables = splitter.split_syllables(args.string)
    
    print(syllables)
