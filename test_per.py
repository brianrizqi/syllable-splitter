from HybridSyllableSplitter import HybridSyllableSplitter

splitter = HybridSyllableSplitter()
words_groups = {
    "Pangkal Verba": ["perbuat", "peroleh"],
    "Pangkal Adjektiva (Kausatif)": [
        "perbesar", "perpanjang", "perlemah", "persempit", "perkaya", 
        "perkuat", "permudah", "percepat", "perbanyak", "persulit"
    ],
    "Pangkal Nomina / Numeralia (dengan memper-)": [
        "memperalat", "mempertuan", "memperistri", "memperdua", "mempertiga"
    ]
}

for group, words in words_groups.items():
    print(f"\n--- {group} ---")
    for word in words:
        result = '-'.join(splitter.split_syllables(word))
        print(f"{word:15} -> {result}")
