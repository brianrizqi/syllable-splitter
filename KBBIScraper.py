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
        Get syllables for a word from KBBI (Backward compatibility).
        
        Args:
            word (str): The word to look up
            
        Returns:
            list: List of syllables from the first entry, or None if not found
        """
        results = self.get_word_info(word)
        if results:
            return results[0]['syllables']
        return None

    def get_word_info(self, word):
        """
        Get full word information from KBBI including multiple entries and meanings.
        
        Args:
            word (str): The word to look up
            
        Returns:
            list: List of dictionaries containing entries with syllables and meanings.
        """
        try:
            # Make request to KBBI
            url = f"{self.base_url}/entri/{word}"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code != 200:
                return []
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all entries (h2)
            entries = soup.find_all('h2')
            
            if not entries:
                return []
            
            results = []
            for entry in entries:
                # Get the text, inserting a space between elements to prevent merging words
                entry_text = entry.get_text(" ", strip=True)
                
                # Extract syllables (format: "ajar (1) » pem.bel.a.jar.an")
                syllable_match = re.search(r'([A-Za-z]+(?:\.[A-Za-z]+)+)', entry_text)
                
                if syllable_match:
                    syllable_string = syllable_match.group(1)
                    syllables = syllable_string.split('.')
                else:
                    # Fallback: if no dots, check if it's a valid single syllable word
                    # Remove "»" and things before it
                    parts = re.split(r'[»/]', entry_text)
                    potential_word = parts[-1].split('(')[0].strip()
                    if potential_word and potential_word.isalpha():
                        syllables = [potential_word]
                    else:
                        continue # Skip entries without clear syllable info
                
                # Find meanings associated with this entry
                meanings = []
                
                # Iterate siblings until next h2
                sibling = entry.find_next_sibling()
                while sibling and sibling.name not in ['h2', 'hr']:
                    # Look for lists (ol or ul) containing meanings
                    if sibling.name in ['ol', 'ul', 'div']:
                        # KBBI uses ol for multiple meanings, ul for single meanings
                        items = sibling.find_all('li')
                        if not items and sibling.name == 'li':
                            items = [sibling]
                        
                        for item in items:
                            # Category (red font)
                            cat_el = item.find('font', color='red')
                            category = cat_el.get_text(strip=True) if cat_el else ""
                            
                            # Label (green font, e.g., ki, ark)
                            label_el = item.find('font', color='green')
                            label = label_el.get_text(strip=True) if label_el else ""
                            
                            # Clean the definition text
                            # We want the text minus categories/labels and "→ Tesaurus" links
                            definition_text = item.get_text(" ", strip=True)
                            
                            # Advanced cleaning: remove category and label strings if they exist at the start
                            if category and definition_text.startswith(category):
                                definition_text = definition_text[len(category):].strip()
                            if label and definition_text.startswith(label):
                                definition_text = definition_text[len(label):].strip()
                            
                            # Remove the "→ Tesaurus" text and symbols
                            definition_text = re.sub(r'→\s*Tesaurus', '', definition_text).strip()
                            
                            if definition_text:
                                meanings.append({
                                    'category': category,
                                    'label': label,
                                    'definition': definition_text
                                })
                    
                    sibling = sibling.find_next_sibling()
                
                results.append({
                    'syllables': syllables,
                    'meanings': meanings,
                    'header': entry_text
                })
            
            return results
            
        except Exception as e:
            print(f"Error scraping KBBI for '{word}': {str(e)}")
            return []

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
    print(f"Mencari '{args.string}' di KBBI online...\n")
    entries = scraper.get_word_info(args.string)
    
    if entries:
        for idx, entry in enumerate(entries):
            print(f"Entry #{idx + 1}: {entry['header']}")
            print(f"Syllables: {'-'.join(entry['syllables'])}")
            if entry['meanings']:
                print("Meanings:")
                for m_idx, m in enumerate(entry['meanings']):
                    cat = f"({m['category']}) " if m['category'] else ""
                    label = f"[{m['label']}] " if m['label'] else ""
                    print(f"  {m_idx + 1}. {cat}{label}{m['definition']}")
            print("-" * 40)
    else:
        print(f"Kata '{args.string}' tidak ditemukan di KBBI atau terjadi error.")

