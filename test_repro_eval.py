from HybridSyllableSplitter import HybridSyllableSplitter

def test_eval_cases():
    splitter = HybridSyllableSplitter()
    
    cases = [
        # Word, Root, Expected Split
        ("penyerta", "serta", ["peng", "ser", "ta"]),
        ("pengetahuan", "tahu", ["peng", "ta", "hu", "an"]),
        ("pengecekan", "cek", ["peng", "cek", "an"]),
        ("mengelak", "elak", ["meng", "e", "lak"]),
        ("mengemban", "emban", ["meng", "em", "ban"]),
        ("mengaji", "kaji", ["meng", "ka", "ji"]),
        ("mengemuka", "kemuka", ["meng", "ke", "mu", "ka"]),
        ("mengesampingkan", "samping", ["meng", "ke", "sam", "ping", "kan"]),
        ("mengaum", "aum", ["meng", "a", "um"]),
        ("menyatakan", "nyata", ["meng", "nya", "ta", "kan"]),
        ("menganga", "nganga", ["meng", "nga", "nga"]),
        ("menerawang", "terawang", ["meng", "te", "ra", "wang"]),
        ("menambat", "tambat", ["meng", "tam", "bat"]),
        ("membuat", "buat", ["meng", "bu", "at"]),
        ("memvalidasi", "validasi", ["meng", "va", "li", "da", "si"]),
        ("mempertinggi", "tinggi", ["meng", "per", "ting", "gi"]),
        ("mempertegas", "tegas", ["meng", "per", "te", "gas"]),
        ("memperdalam", "dalam", ["meng", "per", "da", "lam"]),
        ("mengebom", "bom", ["meng", "bom"]),
        ("mengecek", "cek", ["meng", "cek"]),
        ("mengepel", "pel", ["meng", "pel"]),
        ("mengerem", "rem", ["meng", "rem"]),
        ("mengetik", "ketik", ["meng", "ke", "tik"]),
        ("mengeblok", "blok", ["meng", "blok"]),
        ("mengedrop", "drop", ["meng", "drop"]),
        ("mentransfusi", "transfusi", ["meng", "trans", "fu", "si"]),
        ("mengkhitan", "khitan", ["meng", "khi", "tan"]),
        ("mengecek-ngecek", "cek", ["meng", "cek", "nge", "cek"]),
        ("dibeli", "beli", ["di", "be", "li"]),
        ("dibelakangi", "belakang", ["di", "be", "la", "kang", "i"]),
        ("terasa", "rasa", ["ter", "ra", "sa"]),
        ("teraba", "raba", ["ter", "ra", "ba"]),
        ("tembakkan", "tembak", ["tem", "bak", "kan"]),
        ("tembakan", "tembak", ["tem", "bak", "an"]),
        ("tembaki", "tembak", ["tem", "bak", "i"]),
        ("memarang", "parang", ["meng", "pa", "rang"]),
        ("mengebor", "bor", ["meng", "bor"]),
        ("teramalkan", "ramal", ["ter", "ra", "mal", "kan"]),
        ("mementaskan", "pentas", ["meng", "pen", "tas", "kan"]),
        ("mengejutkan", "kejut", ["meng", "ke", "jut", "kan"]),
        ("mengepakkan", "kepak", ["meng", "ke", "pak", "kan"]),
        ("mengepak", "pak", ["meng", "pak"]),
        ("mengentaskan", "entas", ["meng", "en", "tas", "kan"]),
        ("pertahanan", "tahan", ["per", "ta", "han", "an"]),
        ("mempertahankan", "tahan", ["meng", "per", "ta", "han", "kan"]),
    ]
    
    print(f"{'Kata Uji':<20} | {'Expected':<30} | {'Actual':<30} | Status")
    print("-" * 90)
    
    passed = 0
    for word, root, expected in cases:
        actual = splitter.split_syllables(word)
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        if status == "✅ PASS":
            passed += 1
        print(f"{word:<20} | {str(expected):<30} | {str(actual):<30} | {status}")
    
    print("-" * 90)
    print(f"Passed: {passed}/{len(cases)}")

if __name__ == "__main__":
    test_eval_cases()
