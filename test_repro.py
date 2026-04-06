
from HybridSyllableSplitter import HybridSyllableSplitter

def test_repro():
    splitter = HybridSyllableSplitter()
    
    # Format: (word, expected_syllables, description)
    # Based on the image provided by user
    test_cases = [
        ('beranting', ['ber', 'ran', 'ting'], "ber- + ranting"),
        ('beranting', ['ber', 'an', 'ting'], "ber- + anting"),
        ('berevolusi', ['ber', 'e', 'vo', 'lu', 'si'], "ber- + evolusi"),
        ('beruang', ['ber', 'ru', 'ang'], "ber- + ruang"),
        ('beruang', ['ber', 'u', 'ang'], "ber- + uang"),
        ('belunjur', ['ber', 'un', 'jur'], "ber- + unjur (allomorph bel-)"),
        ('beleter', ['ber', 'le', 'ter'], "ber- + leter"),
        ('belagu', ['ber', 'la', 'gu'], "ber- + lagu"),
        ('bermain', ['ber', 'ma', 'in'], "ber- + main (should not be pain)"),
        ('perendah', ['per', 'ren', 'dah'], "per- + rendah"),
        ('peringan', ['per', 'ri', 'ngan'], "per- + ringan"),
        ('peruncing', ['per', 'run', 'cing'], "per- + runcing"),
    ]
    
    print(f"{'Word':15} | {'Expected':30} | {'Actual':30} | Status")
    print("-" * 90)
    
    for word, expected, desc in test_cases:
        actual = splitter.split_syllables(word)
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        print(f"{word:15} | {str(expected):30} | {str(actual):30} | {status} ({desc})")

if __name__ == "__main__":
    test_repro()
