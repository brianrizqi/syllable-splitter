from HybridSyllableSplitter import HybridSyllableSplitter

def test_full_suite():
    splitter = HybridSyllableSplitter()
    
    # Format: (word, expected_syllables, root_hint=None)
    cases = [
        # Ambiguous ber- cases
        ("beranting", ["ber", "an", "ting"], "anting"),
        ("beranting", ["ber", "ran", "ting"], "ranting"),
        ("berevolusi", ["ber", "e", "vo", "lu", "si"], "evolusi"),
        ("berevolusi", ["ber", "re", "vo", "lu", "si"], "revolusi"),
        ("beruang", ["ber", "u", "ang"], "uang"),
        ("beruang", ["ber", "ru", "ang"], "ruang"),
        ("beruang", ["be", "ru", "ang"], "beruang"),
        
        # Standard cases (from previous suite)
        ("bermain", ["ber", "ma", "in"]),
        ("perendah", ["per", "ren", "dah"]),
        ("peringan", ["per", "ri", "ngan"]),
        ("peruncing", ["per", "run", "cing"]),
        ("penyerta", ["peng", "ser", "ta"]),
        ("pengetahuan", ["peng", "ta", "hu", "an"]),
        ("pengecekan", ["peng", "cek", "an"]),
        ("mengelak", ["meng", "e", "lak"]),
        ("mengemban", ["meng", "em", "ban"]),
        ("mengaji", ["meng", "ka", "ji"]),
        ("mengemuka", ["meng", "ke", "mu", "ka"]),
        ("mengesampingkan", ["meng", "ke", "sam", "ping", "kan"]),
        ("mengaum", ["meng", "a", "um"]),
        ("menyatakan", ["meng", "nya", "ta", "kan"]),
        ("menganga", ["meng", "nga", "nga"]),
        ("menerawang", ["meng", "te", "ra", "wang"]),
        ("menambat", ["meng", "tam", "bat"]),
        ("membuat", ["meng", "bu", "at"]),
        ("memvalidasi", ["meng", "va", "li", "da", "si"]),
        ("mempertinggi", ["meng", "per", "ting", "gi"]),
        ("mempertegas", ["meng", "per", "te", "gas"]),
        ("memperdalam", ["meng", "per", "da", "lam"]),
        ("mengebom", ["meng", "bom"]),
        ("mengecek", ["meng", "cek"]),
        ("mengepel", ["meng", "pel"]),
        ("mengerem", ["meng", "rem"]),
        ("mengetik", ["meng", "ke", "tik"]),
        ("mengeblok", ["meng", "blok"]),
        ("mengedrop", ["meng", "drop"]),
        ("mentransfusi", ["meng", "trans", "fu", "si"]),
        ("mengkhitan", ["meng", "khi", "tan"]),
        ("mengecek-ngecek", ["meng", "cek", "nge", "cek"]),
        ("dibeli", ["di", "be", "li"]),
        ("dibelakangi", ["di", "be", "la", "kang", "i"]),
        ("terasa", ["ter", "ra", "sa"]),
        ("teraba", ["ter", "ra", "ba"]),
        ("tembakkan", ["tem", "bak", "kan"]),
        ("tembakan", ["tem", "bak", "an"]),
        ("tembaki", ["tem", "bak", "i"]),
        ("memarang", ["meng", "pa", "rang"]),
        ("mengebor", ["meng", "bor"]),
        ("teramalkan", ["ter", "ra", "mal", "kan"]),
        ("mementaskan", ["meng", "pen", "tas", "kan"]),
        ("mengejutkan", ["meng", "ke", "jut", "kan"]),
        ("mengepakkan", ["meng", "ke", "pak", "kan"]),
        ("mengepak", ["meng", "pak"]),
        ("mengentaskan", ["meng", "en", "tas", "kan"]),
        ("pertahanan", ["per", "ta", "han", "an"]),
        ("mempertahankan", ["meng", "per", "ta", "han", "kan"]),
        ("mengering", ["meng", "ke", "ring"]),
        ("temurun", ["tu", "em", "run"]),
        ("telunjuk", ["tun", "el", "juk"]),
        ("kelupas", ["ku", "el", "pas"]),
        ("kinerja", ["ker", "er", "ja"]), 
        ("kehausan", ["ke", "ha", "us", "an"]),
        ("tembak-menembak", ["tem", "bak", "meng", "tem", "bak"]),
        ("mengelaborasi", ["meng", "e", "la", "bo", "ra", "si"]),
        ("perasaan", ["peng", "ra", "sa", "an"]),
        ("pekerjaan", ["peng", "ker", "ja", "an"]),
        ("penyebutan", ["peng", "se", "but", "an"]),
        ("pelajar", ["peng", "a", "jar"], "ajar"),
        ("dedaunan", ["de", "da", "un", "an"]),
        ("permainan", ["per", "ma", "in", "an"]),
        ("bersaing", ["ber", "sa", "ing"]),
    ]
    
    print(f"{'Kata Uji':<20} | {'Root Hint':<12} | {'Expected':<30} | {'Actual':<30} | Status")
    print("-" * 120)
    
    passed = 0
    for case in cases:
        word = case[0]
        expected = case[1]
        root_hint = case[2] if len(case) > 2 else None
        
        actual = splitter.split_syllables(word, root_hint=root_hint)
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        if status == "✅ PASS":
            passed += 1
        
        hint_str = root_hint if root_hint else "-"
        print(f"{word:<20} | {hint_str:<12} | {str(expected):<30} | {str(actual):<30} | {status}")
        
    print("-" * 120)
    print(f"Passed: {passed}/{len(cases)}")

if __name__ == "__main__":
    test_full_suite()
