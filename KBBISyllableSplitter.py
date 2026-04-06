# KBBI-Style Syllable Splitter
# Trying to match KBBI output exactly

class KBBISyllableSplitter:
    
    def __init__(self):
        # Vokal (vowels)
        self.vowels = set('aiueo')
        
        # Diftong (diphthongs) - tidak dipenggal
        self.diphthongs = ['ai', 'au', 'ei', 'oi']
        
        # Gabungan konsonan yang melambangkan satu bunyi
        self.consonant_clusters = ['ng', 'ny', 'sy', 'kh']
        
    def is_vowel(self, char):
        """Check if character is a vowel"""
        return char.lower() in self.vowels
    
    def split_syllables(self, word):
        """
        Split word into syllables matching KBBI style
        
        Key insight from KBBI "pembelajaran" = pem.bel.a.jar.an:
        - After 'e' we have 'mb' → split as 'em-b' not 'e-mb'
        - After 'e' we have 'l' → 'bel' not 'be-l'  
        - After 'a' we have 'j' → 'jar' not 'ja-r'
        
        Pattern: When we have VC pattern, keep adding consonants until we hit a vowel,
        then check if we should split before the last consonant or keep it
        """
        if not word:
            return []
        
        word = word.lower()
        syllables = []
        current = ""
        i = 0
        
        while i < len(word):
            current += word[i]
            
            # Check if current char is a vowel and we should consider splitting
            if self.is_vowel(word[i]) and i < len(word) - 1:
                # We just added a vowel, look ahead
                j = i + 1
                consonants_ahead = ""
                
                # Collect all consonants ahead
                while j < len(word) and not self.is_vowel(word[j]):
                    consonants_ahead += word[j]
                    j += 1
                
                # Check if there's a vowel after the consonants
                if j < len(word) and self.is_vowel(word[j]):
                    # We have pattern: V + C+ + V
                    num_consonants = len(consonants_ahead)
                    
                    if num_consonants == 0:
                        # VV pattern - check for diphthongs (ai, au, ei, oi)
                        # They are diphthongs (single sound) usually at the end of base words.
                        # Otherwise (in the middle, or between root/suffix), they are separate syllables.
                        is_diphthong = False
                        if word[i:i+2] in self.diphthongs:
                            if i + 2 == len(word):
                                is_diphthong = True
                            # Loanwords with diphthongs in the middle (boikot, koboi, etc.)
                            elif any(word.endswith(w) for w in ['boikot', 'koboi', 'sepoi', 'konvoi', 'survei']):
                                # Only if the match is at the end or covers the current position
                                part = word[i:]
                                if any(part == w or part.startswith(w) for w in ['boi', 'poi', 'voi', 'vei']):
                                     is_diphthong = True
                         
                        if not is_diphthong:
                            syllables.append(current)
                            current = ""
                    elif num_consonants == 1:
                        # VCV → V-CV (split before consonant)
                        syllables.append(current)
                        current = ""
                    elif num_consonants >= 2:
                        # VCCV or more
                        # Check if consonants form a cluster at the start
                        if consonants_ahead[:2] in self.consonant_clusters:
                            if num_consonants > 2:
                                # Digraph followed by more (e.g. ngg in tinggal)
                                # Take the digraph and split: VC(cluster)-CV
                                current += consonants_ahead[:2]
                                syllables.append(current)
                                current = ""
                                i += 2 # Skip the digraph we just added
                            else:
                                # Just a digraph (e.g. ny in hanya)
                                # V-CCV: split before the digraph
                                syllables.append(current)
                                current = ""
                        else:
                            # VC-CV: take first consonant, leave rest
                            current += consonants_ahead[0]
                            syllables.append(current)
                            current = ""
                            i += 1  # Skip the consonant we just added
            
            i += 1
        
        # Add remaining
        if current:
            syllables.append(current)
        
        return syllables

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Split string into syllables matching KBBI style.")
    parser.add_argument("string", help="string to be splitted.")
    
    args = parser.parse_args()
    
    splitter = KBBISyllableSplitter()
    syllables = splitter.split_syllables(args.string)
    
    print(syllables)
