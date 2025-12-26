# Syllable Rules for Indonesian Language
# Applies PUEBI syllable splitting rules

class SyllableRules:
    
    def __init__(self):
        # Vokal (vowels)
        self.vowels = set('aiueo')
        
        # Diftong (diphthongs) - tidak dipenggal
        self.diphthongs = ['ai', 'au', 'ei', 'oi']
        
        # Gabungan konsonan yang melambangkan satu bunyi
        self.consonant_clusters = ['ng', 'ny', 'sy', 'kh', 'ch']
    
    def is_vowel(self, char):
        """Check if character is a vowel"""
        return char.lower() in self.vowels
    
    def split(self, word):
        """
        Split word into syllables following PUEBI rules
        
        Key rules:
        1. VV (non-diphthong) → V-V (bu-ah, ma-in)
        2. VCV → V-CV (ba-pak, la-wan)
        3. VCCV → VC-CV (man-di, som-bong) - split between consonants
        4. Consonant clusters stay together (ba-nyak, ba-ngsa)
        """
        if not word:
            return []
        
        word = word.lower()
        syllables = []
        current = ""
        i = 0
        
        while i < len(word):
            current += word[i]
            
            # Look ahead to decide if we should split
            if i < len(word) - 1:
                # Rule 1: VV (non-diphthong)
                if self.is_vowel(word[i]) and self.is_vowel(word[i+1]):
                    if word[i:i+2] not in self.diphthongs:
                        syllables.append(current)
                        current = ""
                        i += 1
                        continue
                
                # Rule 2 & 3: Analyze consonant patterns after vowel
                if self.is_vowel(word[i]):
                    # Count consecutive consonants ahead
                    j = i + 1
                    consonants = ""
                    while j < len(word) and not self.is_vowel(word[j]):
                        consonants += word[j]
                        j += 1
                    
                    # Check if there's a vowel after consonants
                    has_vowel_after = j < len(word) and self.is_vowel(word[j])
                    
                    if has_vowel_after and len(consonants) > 0:
                        if len(consonants) == 1:
                            # VCV → V-CV
                            syllables.append(current)
                            current = ""
                        elif len(consonants) >= 2:
                            # Check for consonant cluster
                            cluster = consonants[:2]
                            if cluster in self.consonant_clusters:
                                # V-CCV (keep cluster with next syllable)
                                syllables.append(current)
                                current = ""
                            else:
                                # VCCV → VC-CV (split between consonants)
                                current += consonants[0]
                                syllables.append(current)
                                current = ""
                                i += 1  # Skip the consonant we just added
            
            i += 1
        
        # Add remaining
        if current:
            syllables.append(current)
        
        return syllables

if __name__ == '__main__':
    # Test the syllable rules
    rules = SyllableRules()
    
    test_words = [
        'belajar',
        'Indonesia',
        'komputer',
        'bangunan',
        'membaca',
        'banyak'
    ]
    
    for word in test_words:
        syllables = rules.split(word)
        print(f"{word:15} → {'-'.join(syllables)}")
