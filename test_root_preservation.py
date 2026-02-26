from HybridSyllableSplitter import HybridSyllableSplitter

splitter = HybridSyllableSplitter()
test_cases = {
    "k (meng-)": ["mengerjakan", "mengirimkan", "mengurangi"],
    "p (mem-)": ["memukul", "memasukkan", "memilih"],
    "t (men-)": ["menulis", "menutup", "menerima"],
    "s (meny-)": ["menyapu", "menyiram", "menyusun"],
    "No Peluluhan": ["mengambil", "membantu", "mendengar"],
    "Complex": ["pembelajaran", "memperistri", "diperas"]
}

for group, words in test_cases.items():
    print(f"\n--- {group} ---")
    for word in words:
        result = '-'.join(splitter.split_syllables(word))
        print(f"{word:20} -> {result}")
