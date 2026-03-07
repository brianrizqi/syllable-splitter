import csv
import os
import json
from datetime import datetime
from typing import Optional, Dict, List

class SyllableValidationDB:
    """Handler for syllable validation using Google Sheets (Vercel) or CSV (Local)."""
    
    def __init__(self, db_path: str = "syllable_validations.csv", sheet_name: str = "syllable_validations"):
        """Initialize database handler.
        
        Args:
            db_path: Path to local CSV database file
            sheet_name: Name of the Google Sheet
        """
        self.db_path = db_path
        self.sheet_name = sheet_name
        self.fieldnames = ['word', 'method', 'system_result', 'validation_type', 'final_result', 'timestamp']
        self.is_readonly = False
        
        # Initialize Google Sheets if credentials exist
        self.gc = None
        self.sheet = None
        self._init_google_sheets()
        
        # Fallback to local CSV setup if not using Google Sheets
        if not self.sheet:
            self._ensure_local_database_exists()
    
    def _init_google_sheets(self):
        """Initialize Google Sheets connection from environment variables."""
        creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
        if creds_json:
            try:
                import gspread
                from google.oauth2.service_account import Credentials
                
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                
                creds_dict = json.loads(creds_json)
                credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                self.gc = gspread.authorize(credentials)
                
                # Attempt to open the spreadsheet by name
                spreadsheet = self.gc.open(self.sheet_name)
                self.sheet = spreadsheet.get_worksheet(0)
                
                # Ensure headers exist in the sheet if it's empty
                if not self.sheet.get_all_values():
                    self.sheet.append_row(self.fieldnames)
                
                print(f"✓ Successfully connected to Google Sheets: {self.sheet_name}")
            except Exception as e:
                print(f"⚠ Warning: Google Sheets initialization failed: {e}")
                self.sheet = None
        else:
            # If no credentials, we just use local CSV (no warning needed for local dev)
            pass

    def _ensure_local_database_exists(self):
        """Create local database file with headers if it doesn't exist."""
        if not os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                    writer.writeheader()
            except (OSError, IOError) as e:
                print(f"⚠ Warning: Local database is read-only or inaccessible: {e}")
                self.is_readonly = True

    def add_validation(self, word: str, method: str, system_result: str, 
                       validation_type: str, final_result: str) -> bool:
        """Add a new validation or update existing one."""
        timestamp = datetime.now().isoformat()
        new_record = {
            'word': word,
            'method': method,
            'system_result': system_result,
            'validation_type': validation_type,
            'final_result': final_result,
            'timestamp': timestamp
        }

        # 1. Use Google Sheets if connected
        if self.sheet:
            try:
                self.sheet.append_row([new_record[f] for f in self.fieldnames])
                return True
            except Exception as e:
                print(f"Error saving to Google Sheets: {e}")
                return False

        # 2. Fallback to Local CSV
        if self.is_readonly:
            return False
            
        try:
            records = []
            updated = False
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['word'].lower() == word.lower() and row['method'] == method:
                            records.append(new_record)
                            updated = True
                        else:
                            records.append(row)
            
            if not updated:
                records.append(new_record)
                
            with open(self.db_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(records)
            return True
        except Exception as e:
            print(f"Error saving local validation: {e}")
            return False

    def check_word_exists(self, word: str, method: str = None) -> Optional[Dict]:
        """Check if a word has been validated before."""
        # 1. Check Google Sheets
        if self.sheet:
            try:
                all_records = self.sheet.get_all_records()
                validations = [r for r in all_records if r['word'].lower() == word.lower()]
                if method:
                    validations = [v for v in validations if v['method'] == method]
                return validations[-1] if validations else None
            except Exception as e:
                print(f"Error checking Google Sheets: {e}")

        # 2. Check local CSV
        try:
            with open(self.db_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                validations = []
                for row in reader:
                    if row['word'].lower() == word.lower():
                        if method is None or row['method'] == method:
                            validations.append(row)
                return validations[-1] if validations else None
        except Exception as e:
            return None

    def export_database(self) -> List[Dict]:
        """Export entire database."""
        if self.sheet:
            try:
                return self.sheet.get_all_records()
            except Exception as e:
                print(f"Error exporting Google Sheets: {e}")
                return []
        
        try:
            records = []
            with open(self.db_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
            return records
        except Exception as e:
            return []

    def get_statistics(self) -> Dict:
        """Get database statistics."""
        records = self.export_database()
        if not records:
             return {'total': 0, 'correct': 0, 'corrected': 0, 'methods': {'puebi': 0, 'sylbi': 0, 'kbbi': 0}, 'accuracy_rate': 0}

        total = len(records)
        correct = sum(1 for r in records if r.get('validation_type') == 'correct')
        corrected = sum(1 for r in records if r.get('validation_type') == 'corrected')
        
        methods = {'puebi': 0, 'sylbi': 0, 'kbbi': 0}
        for r in records:
            m = r.get('method', '').lower()
            if m in methods:
                methods[m] += 1
        
        return {
            'total': total,
            'correct': correct,
            'corrected': corrected,
            'methods': methods,
            'accuracy_rate': (correct / total * 100) if total > 0 else 0
        }
