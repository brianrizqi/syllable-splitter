
from HybridSyllableSplitter import HybridSyllableSplitter

def test_full_suite():
    splitter = HybridSyllableSplitter()
    
    cases = [
        # ber- cases
        ("beranting", ["ber", "ran", "ting"]),
        ("berevolusi", ["ber", "e", "vo", "lu", "si"]),
        ("beruang", ["ber", "ru", "ang"]), # (having rooms)
        ("belunjur", ["ber", "un", "jur"]),
        ("beleter", ["ber", "le", "ter"]),
        ("belagu", ["ber", "la", "gu"]),
        ("bermain", ["ber", "ma", "in"]),
        # per- cases
        ("perendah", ["per", "ren", "dah"]),
        ("peringan", ["per", "ri", "ngan"]),
        ("peruncing", ["per", "run", "cing"]),
        # peng- / meng- cases
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
        # memper- cases
        ("mempertinggi", ["meng", "per", "ting", "gi"]),
        ("mempertegas", ["meng", "per", "te", "gas"]),
        ("mempertegas", ["meng", "per", "te", "gas"]),
        ("memperdalam", ["meng", "per", "da", "lam"]),
        # menge- prefix
        ("mengebom", ["meng", "bom"]),
        ("mengecek", ["meng", "cek"]),
        ("mengepel", ["meng", "pel"]),
        ("mengerem", ["meng", "rem"]),
        ("mengetik", ["meng", "ke", "tik"]),
        ("mengeblok", ["meng", "blok"]),
        ("mengedrop", ["meng", "drop"]),
        # Loanwords
        ("mentransfusi", ["meng", "trans", "fu", "si"]),
        ("mengkhitan", ["meng", "khi", "tan"]),
        ("mengecek-ngecek", ["meng", "cek", "nge", "cek"]),
        # di- / ter- / suffixes
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
        # Others
        ("pertahanan", ["per", "ta", "han", "an"]),
        ("mempertahankan", ["meng", "per", "ta", "han", "kan"]),
        ("mengering", ["meng", "ke", "ring"]),
        ("temurun", ["tu", "em", "run"]),
        ("telunjuk", ["tun", "el", "juk"]),
        ("kelupas", ["ku", "el", "pas"]),
        ("kinerja", ["ker", "er", "ja"]), 
        ("kinerja", ["ker", "er", "ja"]),
        ("kehausan", ["ke", "ha", "us", "an"]),
        ("tembak-menembak", ["tem", "bak", "meng", "tem", "bak"]),
        ("mengelaborasi", ["meng", "e", "la", "bo", "ra", "si"]),
        ("perasaan", ["peng", "ra", "sa", "an"]),
        ("pekerjaan", ["peng", "ker", "ja", "an"]),
        ("penyebutan", ["peng", "se", "but", "an"]),
        ("pelajar", ["peng", "la", "jar"]),
        ("dedaunan", ["de", "da", "un", "an"]),
        ("sungai", ["su", "ngai"]),
        ("lihai", ["li", "hai"]),
        ("permainan", ["per", "ma", "in", "an"]),
        ("bersaing", ["ber", "sa", "ing"]),
        ("sepoi", ["se", "poi"]),
        ("konvoi", ["kon", "voi"]),
        ("survei", ["sur", "vei"]),
    ]
    
    print(f"{'Kata Uji':<20} | {'Expected':<35} | {'Actual':<35} | Status")
    print("-" * 110)
    
    passed = 0
    for word, expected in cases:
        actual = splitter.split_syllables(word)
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        if status == "✅ PASS":
            passed += 1
        print(f"{word:<20} | {str(expected):<35} | {str(actual):<35} | {status}")
        
    print("-" * 110)
    print(f"Passed: {passed}/{len(cases)}")

if __name__ == "__main__":
    test_full_suite()
