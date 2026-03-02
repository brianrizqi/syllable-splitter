from HybridSyllableSplitter import HybridSyllableSplitter

splitter = HybridSyllableSplitter()
words = {
    'dipakai': 'di-pa-kai',
    'ditembak': 'di-tem-bak',
    'diberhentikan': 'di-ber-hen-ti-kan',
    'diperbesar': 'di-per-be-sar',
    'ditempati': 'di-tem-pat-i',
    'dimandikan': 'di-man-di-kan',
    'ditinggal': 'di-ting-gal',
    'ditinggalkan': 'di-ting-gal-kan'
}

all_passed = True
for word, expected in words.items():
    result = '-'.join(splitter.split_syllables(word))
    status = "✅ PASS" if result == expected else f"❌ FAIL (Expected: {expected})"
    print(f"{word:15} -> {result:18} {status}")
    if result != expected:
        all_passed = False

if all_passed:
    print("\nAll di- tests passed successfully!")
else:
    print("\nSome tests failed.")
