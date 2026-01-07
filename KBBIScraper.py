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
