import csv
import os
from datetime import datetime
from typing import Optional, Dict, List

class SyllableValidationDB:
    """Handler for syllable validation CSV database."""
    
    def __init__(self, db_path: str = "syllable_validations.csv"):
        """Initialize database handler.
        
        Args:
            db_path: Path to CSV database file
        """
        self.db_path = db_path
        self.fieldnames = [
            'word', 
            'method', 
            'system_result', 
            'validation_type', 
            'final_result', 
            'timestamp'
        ]
        self.is_readonly = False
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database file with headers if it doesn't exist."""
        if not os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                    writer.writeheader()
            except (OSError, IOError) as e:
                print(f"⚠ Warning: Database is read-only or inaccessible: {e}")
                self.is_readonly = True
    
    def add_validation(self, word: str, method: str, system_result: str, 
                      validation_type: str, final_result: str) -> bool:
        """Add a new validation or update existing one (deduplication).
        
        Args:
            word: Original word
            method: Method used (puebi/sylbi/kbbi)
            system_result: System's syllable split result (with hyphens)
            validation_type: 'correct' or 'corrected'
            final_result: Final result (same as system if correct, or user's correction)
        
        Returns:
            True if successful, False otherwise
        """
        if self.is_readonly:
            return False
            
        try:
            timestamp = datetime.now().isoformat()
            new_record = {
                'word': word,
                'method': method,
                'system_result': system_result,
                'validation_type': validation_type,
                'final_result': final_result,
                'timestamp': timestamp
            }
            
            # Read all records
            records = []
            updated = False
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Check for existing word-method pair
                        if row['word'].lower() == word.lower() and row['method'] == method:
                            records.append(new_record)
                            updated = True
                        else:
                            records.append(row)
            
            if not updated:
                records.append(new_record)
                
            # Write back all records
            with open(self.db_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(records)
            return True
        except (OSError, IOError) as e:
            print(f"⚠ Warning: Could not save validation to {self.db_path}: {e}")
            self.is_readonly = True
            return False
        except Exception as e:
            print(f"Error saving validation: {e}")
            return False
    
    def check_word_exists(self, word: str, method: str = None) -> Optional[Dict]:
        """Check if a word has been validated before.
        
        Args:
            word: Word to check
            method: Optional method filter
        
        Returns:
            Dictionary with validation info if found, None otherwise
        """
        try:
            with open(self.db_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Get all validations for this word (most recent first)
                validations = []
                for row in reader:
                    if row['word'].lower() == word.lower():
                        if method is None or row['method'] == method:
                            validations.append(row)
                
                if validations:
                    # Return most recent validation
                    return validations[-1]
                
                return None
        except Exception as e:
            print(f"Error checking word: {e}")
            return None
    
    def get_word_history(self, word: str) -> List[Dict]:
        """Get all validation history for a word.
        
        Args:
            word: Word to get history for
        
        Returns:
            List of validation records
        """
        try:
            history = []
            with open(self.db_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['word'].lower() == word.lower():
                        history.append(row)
            return history
        except Exception as e:
            print(f"Error getting word history: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            total = 0
            correct = 0
            corrected = 0
            methods = {'puebi': 0, 'sylbi': 0, 'kbbi': 0}
            
            with open(self.db_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total += 1
                    if row['validation_type'] == 'correct':
                        correct += 1
                    elif row['validation_type'] == 'corrected':
                        corrected += 1
                    
                    if row['method'] in methods:
                        methods[row['method']] += 1
            
            return {
                'total': total,
                'correct': correct,
                'corrected': corrected,
                'methods': methods,
                'accuracy_rate': (correct / total * 100) if total > 0 else 0
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'total': 0,
                'correct': 0,
                'corrected': 0,
                'methods': {'puebi': 0, 'sylbi': 0, 'kbbi': 0},
                'accuracy_rate': 0
            }
    
    def export_database(self) -> List[Dict]:
        """Export entire database.
        
        Returns:
            List of all validation records
        """
        try:
            records = []
            with open(self.db_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
            return records
        except Exception as e:
            print(f"Error exporting database: {e}")
            return []
