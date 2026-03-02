from HybridSyllableSplitter import HybridSyllableSplitter

splitter = HybridSyllableSplitter()
words = {
    'membuka': 'mem-bu-ka',
    'menutup': 'me-nu-tup',
    'membangun': 'mem-ba-ngun',
    'mendorong': 'men-do-rong',
    'memukul': 'me-mu-kul',
    'menghitung': 'meng-hi-tung'
}

all_passed = True
for word, expected in words.items():
    result = '-'.join(splitter.split_syllables(word))
    status = "✅ PASS" if result == expected else f"❌ FAIL (Expected: {expected})"
    print(f"{word:12} -> {result:15} {status}")
    if result != expected:
        all_passed = False

if all_passed:
    print("\nAll meng- tests passed successfully!")
else:
    print("\nSome tests failed.")
