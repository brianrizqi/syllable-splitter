
from HybridSyllableSplitter import HybridSyllableSplitter

def test_cases():
    splitter = HybridSyllableSplitter()
    
    cases = [
        # Word, Expected Syllables (Joined with '.')
        ("mengering", "meng.ke.ring"),
        ("temurun", "tu.em.run"),
        ("telunjuk", "tun.el.juk"),
        ("kelupas", "ku.el.pas"),
        ("kinerja", "ker.er.ja"),
        ("kehausan", "ke.ha.us.an"),
        ("tembak-menembak", "tem.bak.meng.tem.bak"),
        ("mengelaborasi", "meng.e.la.bo.ra.si"),
        ("perasaan", "peng.ra.sa.an"),
        ("pekerjaan", "peng.ker.ja.an"),
        ("penyebutan", "peng.se.but.an"),
        ("pelajar", "peng.la.jar"),
        ("dedaunan", "de.da.un.an"),
        ("sungai", "su.ngai"),
        ("lihai", "li.hai"),
        ("permainan", "per.ma.in.an"),
        ("bersaing", "ber.sa.ing"),
        ("sepoi", "se.poi"),
        ("konvoi", "kon.voi"),
        ("survei", "sur.vei"),
    ]
    
    print(f"{'Word':<20} | {'Expected':<30} | {'Actual':<30} | Status")
    print("-" * 100)
    
    for word, expected in cases:
        actual_list = splitter.split_syllables(word)
        # Filter out spaces for comparison if any
        actual_list = [s for s in actual_list if s.strip()]
        actual = ".".join(actual_list)
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        print(f"{word:<20} | {expected:<30} | {actual:<30} | {status}")

if __name__ == "__main__":
    test_cases()
