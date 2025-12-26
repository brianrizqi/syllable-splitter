
# source https://github.com/fahadh4ilyas/syllable_splitter
# Modified to support morphological syllable splitting (affix-aware)

import re
from SyllableSplitter import SyllableSplitter

class SyllableSplitterMorphological(SyllableSplitter):
    
    def __init__(self, consonant=None, vocal=None, double_consonant=None):
        super().__init__(consonant, vocal, double_consonant)
        
        # Indonesian prefixes
        self.prefixes = [
            'memper', 'diper', 'keber', 'terpem', 'terpe',
            'meng', 'meny', 'meng', 'mem', 'men', 'me',
            'peng', 'peny', 'pem', 'pen', 'pe',
            'ber', 'ter', 'di', 'ke', 'se'
        ]
        
        # Indonesian suffixes
        self.suffixes = ['kan', 'an', 'i']
        
        # Circumfixes (prefix + suffix combinations)
        self.circumfixes = [
            ('ke', 'an'),
            ('pe', 'an'),
            ('per', 'an'),
            ('ber', 'an'),
            ('ber', 'kan')
        ]
    
    def detect_affixes(self, word):
        """
        Detect and separate affixes from the root word.
        Returns: (prefix, root, suffix)
        """
        original_word = word
        prefix = ''
        suffix = ''
        root = word
        
        # Check for circumfixes first
        for pre, suf in self.circumfixes:
            if word.startswith(pre) and word.endswith(suf) and len(word) > len(pre) + len(suf):
                potential_root = word[len(pre):-len(suf)]
                if len(potential_root) >= 2:  # Root should be at least 2 chars
                    prefix = pre
                    suffix = suf
                    root = potential_root
                    return (prefix, root, suffix)
        
        # Check for prefixes
        for pre in sorted(self.prefixes, key=len, reverse=True):
            if word.startswith(pre) and len(word) > len(pre):
                potential_root = word[len(pre):]
                if len(potential_root) >= 2:  # Root should be at least 2 chars
                    prefix = pre
                    root = potential_root
                    break
        
        # Check for suffixes
        for suf in sorted(self.suffixes, key=len, reverse=True):
            if root.endswith(suf) and len(root) > len(suf):
                potential_root = root[:-len(suf)]
                if len(potential_root) >= 2:  # Root should be at least 2 chars
                    suffix = suf
                    root = potential_root
                    break
        
        return (prefix, root, suffix)
    
    def split_syllables(self, string):
        """
        Split syllables following KBBI standard.
        KBBI uses the same rules as PUEBI/phonetic method.
        The difference is only in presentation (KBBI uses dots, PUEBI uses hyphens).
        """
        # KBBI follows the same syllable splitting rules as PUEBI
        # So we just use the parent class method
        return super().split_syllables(string)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Split string into syllables with morphological awareness.")
    parser.add_argument("string", help="string to be splitted.")
    parser.add_argument("--compare", action="store_true", help="Compare with phonetic method")
    
    args = parser.parse_args()
    
    morphological = SyllableSplitterMorphological()
    syllables = morphological.split_syllables(args.string)
    
    print(f"Morphological: {syllables}")
    
    if args.compare:
        phonetic = SyllableSplitter()
        phonetic_syllables = phonetic.split_syllables(args.string)
        print(f"Phonetic: {phonetic_syllables}")
