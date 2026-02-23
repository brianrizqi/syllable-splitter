from HybridSyllableSplitter import HybridSyllableSplitter

splitter = HybridSyllableSplitter()
words_groups = {
    "Pangkal Verba": [
        "mengerjakan", "menyelesaikan", "membolehkan", "melemparkan", "meninggalkan",
        "memukulkan", "menikamkan", "mengikatkan", "membalutkan",
        "mengambilkan", "membuatkan", "memilihkan", "membukakan"
    ],
    "Kausatif / Emosional": [
        "mengamankan", "membebaskan", "memuaskan", "mengagumkan", "memalukan",
        "menyenangkan", "mencemaskan", "mengejutkan", "menyedihkan", "menakutkan",
        "merindukan", "membanggakan"
    ],
    "Pangkal Nomina / Numeralia": [
        "mengandangkan", "mementaskan", "meliburkan", "meminggirkan",
        "merajakan", "mendoktorkan", "mencalonkan", "mengorbankan", 
        "menghadiahkan", "merencanakan", "mendewakan", "menyukseskan"
    ],
    "Kompleks per- -kan": [
        "pertemukan", "pertarungkan", "pertanggungjawabkan", "pertahankan", 
        "perhentikan", "perbandingkan", "peristrikan"
    ],
    "Preposisional ke- -kan": [
        "mengemukakan", "mengetengahkan", "mengeluarkan", "mengedepankan", "mengesampingkan"
    ]
}

for group, words in words_groups.items():
    print(f"\n--- {group} ---")
    for word in words:
        result = '-'.join(splitter.split_syllables(word))
        print(f"{word:20} -> {result}")
