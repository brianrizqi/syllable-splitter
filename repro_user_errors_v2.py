from HybridSyllableSplitter import HybridSyllableSplitter

def test():
    splitter = HybridSyllableSplitter()
    test_cases = [
        # (word, root_hint, expected)
        ("beranting", "anting", "ber.an.ting"),
        ("menguatkan", "kuat", "meng.ku.at.kan"),
        ("memerah", "merah", "meng.me.rah"),
        ("memerah", "perah", "meng.pe.rah"),
        ("mengukur", "ukur", "meng.u.kur"),
        ("mengukur", "kukur", "meng.ku.kur"),
        ("mengokang", "kokang", "meng.ko.kang"),
        ("dikokang", "kokang", "di.ko.kang"),
        ("mengkerut", "kerut", "meng.ke.rut"),
        ("berkerut", "kerut", "ber.ke.rut"),
        ("gelegar", "gegar", "ge.el.gar"),
        ("gelegar", "gelegar", "ge.le.gar"),
        ("mengompori", "kompor", "meng.kom.por.i"),
    ]
    
    print(f"{'Word':<15} | {'Root Hint':<10} | {'Expected':<20} | {'Actual':<20} | {'Status'}")
    print("-" * 80)
    for word, root, expected in test_cases:
        actual = ".".join(splitter.split_syllables(word, root_hint=root))
        status = "✅" if actual == expected else "❌"
        print(f"{word:<15} | {root:<10} | {expected:<20} | {actual:<20} | {status}")

if __name__ == "__main__":
    test()
