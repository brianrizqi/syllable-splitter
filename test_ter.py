from HybridSyllableSplitter import HybridSyllableSplitter

splitter = HybridSyllableSplitter()
words_groups = {
    "Perfektif / Passive": [
        "terletak", "tertulis", "terbuka", "tercatat", "terputus", 
        "terkenal", "terhormat", "terhubung", "tercemar"
    ],
    "Ketidaksengajaan": [
        "tertinggal", "terjatuh", "terbawa", "terpakai", "tersebat", "tertangkap"
    ],
    "Kemampuan (Ketakmampuan)": [
        "terbeli", "terdengar", "terpecahkan", "terhitung", "tertahankan", 
        "terselesaikan", "terpisahkan", "terbantahkan", "terelakkan"
    ],
    "Gramatikalisasi": [
        "tertawa", "terhadap", "terlalu", "termasuk", "terlambat"
    ]
}

for group, words in words_groups.items():
    print(f"\n--- {group} ---")
    for word in words:
        result = '-'.join(splitter.split_syllables(word))
        print(f"{word:15} -> {result}")
