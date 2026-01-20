import requests
from bs4 import BeautifulSoup
import re

class KBBIScraper:
    """
    Simple KBBI scraper to get syllable information from KBBI online dictionary.
    Uses the new KBBI URL: https://kbbi.kemendikdasmen.go.id
    """
    
    def __init__(self):
        self.base_url = "https://kbbi.kemendikdasmen.go.id"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_syllables(self, word):
        """
        Get syllables for a word from KBBI.
        
        Args:
            word (str): The word to look up
            
        Returns:
            list: List of syllables, or None if not found
        """
        try:
            # Make request to KBBI
            url = f"{self.base_url}/entri/{word}"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code != 200:
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the syllable information
            # KBBI displays syllables in format like "pem.bel.a.jar.an"
            # Look for the main entry heading
            entry = soup.find('h2')
            
            if not entry:
                return None
            
            # Get the text which contains syllables
            entry_text = entry.get_text(strip=True)
            
            # Extract syllables (format: "ajar (1) » pem.bel.a.jar.an")
            # or sometimes just "pem.bel.a.jar.an"
            syllable_match = re.search(r'([a-z]+(?:\.[a-z]+)+)', entry_text)
            
            if syllable_match:
                syllable_string = syllable_match.group(1)
                # Split by dots to get individual syllables
                syllables = syllable_string.split('.')
                return syllables
            
            return None
            
        except Exception as e:
            print(f"Error scraping KBBI for '{word}': {str(e)}")
            return None

if __name__ == '__main__':
    import argparse
    from SpellChecker import IndonesianSpellChecker
    
    parser = argparse.ArgumentParser(description="Get syllables from KBBI online dictionary.")
    parser.add_argument("string", help="word to look up in KBBI")
    parser.add_argument("--no-spell-check", action="store_true", help="Skip spell checking")
    
    args = parser.parse_args()
    
    # Spell check first (unless disabled)
    if not args.no_spell_check:
        spell_checker = IndonesianSpellChecker()
        errors = spell_checker.check_text(args.string)
        
        if errors:
            print("\n⚠️  PERINGATAN DETEKSI KATA:")
            print("=" * 60)
            
            # Categorize errors
            typos = [e for e in errors if e.get('error_type') == 'typo']
            not_found = [e for e in errors if e.get('error_type') == 'not_found']
            non_indonesian = [e for e in errors if e.get('error_type') == 'non_indonesian']
            
            # Colors for terminal
            RED = '\033[91m'
            YELLOW = '\033[93m'
            BLUE = '\033[94m'
            RESET = '\033[0m'
            BOLD = '\033[1m'
            
            if non_indonesian:
                print(f"\n{BLUE}{BOLD}🔵 Bukan Bahasa Indonesia:{RESET}")
                for error in non_indonesian:
                    print(f"  • {BOLD}{error['word']}{RESET} - {error['reason']}")
            
            if typos:
                print(f"\n{RED}{BOLD}🔴 Kemungkinan Typo:{RESET}")
                for error in typos:
                    print(f"  • {BOLD}{error['word']}{RESET} - {error['reason']}")
                    if error.get('suggestions'):
                        print(f"    Saran: {', '.join(error['suggestions'])}")
            
            if not_found:
                print(f"\n{YELLOW}{BOLD}🟡 Tidak Ditemukan di KBBI:{RESET}")
                for error in not_found:
                    print(f"  • {BOLD}{error['word']}{RESET}")
                    if error.get('suggestions'):
                        print(f"    Saran: {', '.join(error['suggestions'])}")
            
            print("\n" + "=" * 60)
            response = input("Lanjutkan pencarian di KBBI? (y/n): ")
            if response.lower() != 'y':
                print("Dibatalkan.")
                exit(0)
            print()
    
    scraper = KBBIScraper()
    print(f"Mencari '{args.string}' di KBBI online...")
    syllables = scraper.get_syllables(args.string)
    
    if syllables:
        print(f"Result: {syllables}")
        print(f"Joined: {'-'.join(syllables)}")
    else:
        print(f"Kata '{args.string}' tidak ditemukan di KBBI atau terjadi error.")

