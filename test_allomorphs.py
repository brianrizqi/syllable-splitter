
from HybridSyllableSplitter import HybridSyllableSplitter

def test_allomorphs():
    splitter = HybridSyllableSplitter()
    
    test_cases = [
        # meng- variants
        ('mengecat', ['meng', 'nge', 'cat']), # Preserve 3 syllables
        ('mengambil', ['meng', 'am', 'bil']),
        ('membaca', ['meng', 'ba', 'ca']),
        ('menulis', ['meng', 'tu', 'lis']),
        ('menyapu', ['meng', 'sa', 'pu']),
        
        # peng- variants
        ('pengepak', ['peng', 'nge', 'pak']),
        ('penyestok', ['peng', 'nyes', 'tok']),
        ('pembaca', ['peng', 'ba', 'ca']),
        ('penulis', ['peng', 'tu', 'lis']),
        ('penyapu', ['peng', 'sa', 'pu']),
        ('pembuatan', ['peng', 'bu', 'at', 'an']),
        ('penyempurnaan', ['peng', 'sem', 'pur', 'na', 'an']),
        ('menyempurnakan', ['meng', 'sem', 'pur', 'na', 'kan']),
        
        # per- variants
        ('pelajar', ['per', 'a', 'jar']),
        ('pesilat', ['per', 'si', 'lat']),
        
        # ber- variants
        ('belajar', ['ber', 'a', 'jar']),
        ('bekerja', ['ber', 'ker', 'ja']),
        
        # ter- variants
        ('tertawa', ['ter', 'ta', 'wa']),
        ('teperdaya', ['ter', 'per', 'da', 'ya'])
    ]
    
    print(f"{'Word':20} | {'Expected':30} | {'Result':30} | Status")
    print("-" * 100)
    
    passed = 0
    for word, expected in test_cases:
        result = splitter.split_syllables(word)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        if result == expected:
            passed += 1
        print(f"{word:20} | {str(expected):30} | {str(result):30} | {status}")
    
    print("-" * 100)
    print(f"Passed: {passed}/{len(test_cases)}")

if __name__ == "__main__":
    test_allomorphs()
