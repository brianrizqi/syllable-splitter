# 📚 RULES.MD - Dokumentasi Aturan Syllable Splitter

**Aplikasi Pemisah Suku Kata Bahasa Indonesia**  
**Untuk Presentasi Akademik**

---

## 📋 Daftar Isi

1. [Ringkasan Sistem](#ringkasan-sistem)
2. [Arsitektur Aplikasi](#arsitektur-aplikasi)
3. [Aturan Pemisahan Suku Kata](#aturan-pemisahan-suku-kata)
4. [Algoritma dan Implementasi](#algoritma-dan-implementasi)
5. [Analisis Morfologi](#analisis-morfologi)
6. [Spell Checker](#spell-checker)
7. [API Endpoints](#api-endpoints)
8. [Teknologi dan Dependencies](#teknologi-dan-dependencies)

---

## 1. Ringkasan Sistem

### 1.1 Tujuan Aplikasi
Aplikasi web untuk memisahkan kata bahasa Indonesia menjadi suku kata menggunakan dua metode berbeda:
- **PUEBI** (Pedoman Umum Ejaan Bahasa Indonesia) - Metode resmi pemerintah
- **KBBI** (Kamus Besar Bahasa Indonesia) - Metode hybrid dengan analisis morfologi

### 1.2 Fitur Utama
- ✅ Dua metode pemisahan (PUEBI & KBBI)
- ✅ Spell checker untuk deteksi typo
- ✅ Analisis morfologi (prefix, infix, root, suffix)
- ✅ Exception dictionary untuk kata-kata khusus
- ✅ Web interface modern dengan Flask
- ✅ Real-time processing tanpa reload halaman

---

## 2. Arsitektur Aplikasi

### 2.1 Struktur File

```
Syllable Splitter/
├── app.py                          # Flask application (entry point)
├── requirements.txt                # Python dependencies
│
├── Core Modules/
│   ├── PUEBIOfficialSplitter.py   # Implementasi aturan PUEBI
│   ├── HybridSyllableSplitter.py  # Metode KBBI (hybrid)
│   ├── KBBISyllableSplitter.py    # Syllable rules untuk KBBI
│   ├── SyllableSplitter.py        # Base class (dari library asli)
│   ├── MorphologicalAnalyzer.py   # Analisis morfologi dengan nlp-id
│   ├── SpellChecker.py            # Deteksi typo
│   ├── SyllableRules.py           # Aturan syllable PUEBI
│   └── exceptions.json            # Dictionary kata-kata khusus
│
├── templates/
│   └── index.html                 # Frontend HTML
│
└── static/
    └── style.css                  # CSS styling
```

### 2.2 Flow Diagram

```
User Input → Spell Check (optional) → Method Selection → Processing → Output
                                           ↓
                                    PUEBI / KBBI
                                           ↓
                              Syllable Splitting Algorithm
                                           ↓
                                   JSON Response
```

---

## 3. Aturan Pemisahan Suku Kata

### 3.1 Aturan PUEBI (Pedoman Umum Ejaan Bahasa Indonesia)

Berdasarkan dokumen resmi PUEBI dari Kemendikbud:

#### **Rule 1: VV (Vokal-Vokal) Non-Diftong**
- **Aturan**: Dua vokal yang bukan diftong dipisahkan
- **Pola**: `V-V`
- **Contoh**: 
  - `buah` → `bu-ah`
  - `main` → `ma-in`

#### **Rule 2: Diftong**
- **Aturan**: Diftong TIDAK dipisahkan
- **Diftong**: `ai`, `au`, `ei`, `oi`
- **Contoh**:
  - `pandai` → `pan-dai` (bukan `pan-da-i`)
  - `saudara` → `sau-da-ra` (bukan `sa-u-da-ra`)

#### **Rule 3: VCV (Vokal-Konsonan-Vokal)**
- **Aturan**: Pisahkan sebelum konsonan
- **Pola**: `V-CV`
- **Contoh**:
  - `bapak` → `ba-pak`
  - `lawan` → `la-wan`

#### **Rule 4: VCCV (Vokal-Konsonan-Konsonan-Vokal)**
- **Aturan**: Pisahkan di antara dua konsonan
- **Pola**: `VC-CV`
- **Contoh**:
  - `mandi` → `man-di`
  - `sombong` → `som-bong`

#### **Rule 5: VCCCV (Vokal-Konsonan-Konsonan-Konsonan-Vokal)**
- **Aturan**: Pisahkan setelah konsonan pertama
- **Pola**: `VC-CCV`
- **Contoh**:
  - `instrumen` → `in-stru-men`
  - `ultra` → `ul-tra`

#### **Rule 6: Consonant Clusters**
- **Aturan**: Gabungan konsonan yang melambangkan satu bunyi TIDAK dipisahkan
- **Clusters**: `ng`, `ny`, `sy`, `kh`, `ch`, `dh`, `gh`, `ph`, `sh`, `th`
- **Contoh**:
  - `banyak` → `ba-nyak` (bukan `ban-yak`)
  - `makhuk` → `makh-luk` (bukan `mak-hluk`)

### 3.2 Aturan KBBI (Hybrid Morphological-Syllable)

Metode KBBI menggunakan pendekatan hybrid yang menggabungkan:

#### **Step 1: Exception Dictionary Check**
- Cek apakah kata ada di `exceptions.json`
- Jika ada, gunakan pemisahan yang sudah didefinisikan
- Contoh:
  ```json
  {
    "belajar": ["bel", "a", "jar"],
    "tangan": ["ta", "ngan"]
  }
  ```

#### **Step 2: Morphological Analysis**
- Deteksi prefix, root, suffix menggunakan `nlp-id` lemmatizer
- Dekomposisi prefix untuk menemukan infix
- Contoh: `pembelajaran`
  - Prefix: `pe`
  - Infix: `m`
  - Root: `belajar`
  - Suffix: `an`

#### **Step 3: Infix Extraction**
- Ekstrak nasal consonants (`m`, `n`, `ng`, `ny`) dari root jika prefix adalah `pe`, `be`, `me`
- Contoh: `membaca`
  - Prefix: `me`
  - Infix: `m` (extracted from root)
  - Root: `baca`

#### **Step 4: Syllable Splitting per Morpheme**
- Terapkan aturan syllable pada setiap morpheme
- Gabungkan hasil

#### **Hasil Perbandingan**:
```
Input: "pembelajaran"

PUEBI: pem-be-la-ja-ran
KBBI:  pe-m-bel-a-jar-an
       ↑   ↑   ↑       ↑
       |   |   |       └─ suffix
       |   |   └───────── root (dari exception)
       |   └───────────── infix
       └───────────────── prefix
```

---

## 4. Algoritma dan Implementasi

### 4.1 PUEBIOfficialSplitter Algorithm

```python
def split_syllables(word):
    """
    Implementasi aturan PUEBI
    """
    syllables = []
    current = ""
    i = 0
    
    while i < len(word):
        current += word[i]
        
        if is_vowel(word[i]) and i < len(word) - 1:
            # Count consonants ahead
            consonants = count_consonants_ahead(word, i+1)
            
            if len(consonants) == 0:
                # VV pattern - check diphthong
                if not is_diphthong(word[i:i+2]):
                    syllables.append(current)
                    current = ""
            
            elif len(consonants) == 1:
                # VCV → V-CV
                syllables.append(current)
                current = ""
            
            elif len(consonants) >= 2:
                # Check for consonant cluster
                if is_cluster(consonants[:2]):
                    # V-CCV
                    syllables.append(current)
                    current = ""
                else:
                    # VC-CV
                    current += consonants[0]
                    syllables.append(current)
                    current = ""
                    i += 1
        
        i += 1
    
    if current:
        syllables.append(current)
    
    return syllables
```

**Kompleksitas**: O(n²) dimana n = panjang kata

### 4.2 HybridSyllableSplitter Algorithm

```python
def split_syllables(word):
    """
    Hybrid approach: Morphology + Syllable
    """
    # Step 1: Check exceptions
    if word in exceptions:
        return exceptions[word]
    
    # Step 2: Morphological analysis
    prefix, detected_root, suffix, lemma = analyze_with_lemmatizer(word)
    
    result = []
    
    # Step 3: Decompose prefix
    if prefix:
        base_prefix, infix = decompose_prefix(prefix)
        if infix:
            result.append(base_prefix)
            result.append(infix)
        else:
            result.extend(split_syllables_kbbi(prefix))
    
    # Step 4: Extract infix from root
    if detected_root and prefix in ['pe', 'be', 'me']:
        nasal_consonants = ['ng', 'ny', 'm', 'n']
        for nasal in nasal_consonants:
            if detected_root.startswith(nasal):
                result.append(nasal)
                detected_root = detected_root[len(nasal):]
                break
    
    # Step 5: Split root
    if detected_root:
        if detected_root in exceptions:
            result.extend(exceptions[detected_root])
        else:
            result.extend(split_syllables_kbbi(detected_root))
    
    # Step 6: Add suffix
    if suffix:
        result.append(suffix)
    
    return result
```

**Kompleksitas**: O(n²) + O(lemmatizer)

### 4.3 KBBISyllableSplitter Algorithm

Menggunakan aturan yang sama dengan PUEBI tetapi dengan pendekatan yang sedikit berbeda dalam menangani pola VCCV:

```python
def split_syllables(word):
    """
    KBBI-style syllable splitting
    Pola: VC-CV (ambil konsonan pertama, sisakan yang lain)
    """
    syllables = []
    current = ""
    i = 0
    
    while i < len(word):
        current += word[i]
        
        if is_vowel(word[i]) and i < len(word) - 1:
            consonants_ahead = collect_consonants(word, i+1)
            
            if has_vowel_after(consonants_ahead):
                num_consonants = len(consonants_ahead)
                
                if num_consonants == 1:
                    # VCV → V-CV
                    syllables.append(current)
                    current = ""
                
                elif num_consonants >= 2:
                    if is_cluster(consonants_ahead[:2]):
                        # V-CCV
                        syllables.append(current)
                        current = ""
                    else:
                        # VC-CV
                        current += consonants_ahead[0]
                        syllables.append(current)
                        current = ""
                        i += 1
        
        i += 1
    
    if current:
        syllables.append(current)
    
    return syllables
```

---

## 5. Analisis Morfologi

### 5.1 Morpheme Types

#### **Prefix (Awalan)**
```python
prefixes = [
    # Complex prefixes
    'memper', 'diper', 'keber', 'terpem', 'terpe',
    'mempel', 'mempe', 'pember', 'penge',
    
    # Nasal prefixes
    'meng', 'meny', 'mem', 'men', 'me',
    'peng', 'peny', 'pem', 'pen', 'pe',
    
    # Other prefixes
    'ber', 'ter', 'per', 'di', 'ke', 'se'
]
```

#### **Suffix (Akhiran)**
```python
suffixes = [
    # Derivational
    'kan', 'an', 'i',
    
    # Particles
    'lah', 'kah', 'tah', 'pun',
    
    # Possessive
    'ku', 'mu', 'nya'
]
```

#### **Circumfix (Konfiks)**
```python
circumfixes = [
    ('ke', 'an'),      # kebersamaan
    ('pe', 'an'),      # pembelajaran
    ('per', 'an'),     # perjalanan
    ('ber', 'an'),     # bersamaan
    ('ber', 'kan'),    # berdasarkan
    ('me', 'kan'),     # membacakan
    ('di', 'kan'),     # dibacakan
    ('ter', 'kan'),    # terbuktikan
]
```

### 5.2 Infix Detection

**Infix** adalah sisipan yang muncul di dalam prefix. Dalam bahasa Indonesia, infix muncul sebagai nasal assimilation:

```python
def decompose_prefix(prefix):
    """
    Dekomposisi prefix menjadi base + infix
    
    Contoh:
    - pem → pe + m
    - pel → pe + l
    - per → pe + r
    - mem → me + m
    - ber → be + r
    """
    base_prefixes = ['pe', 'be', 'me']
    infixes = ['m', 'l', 'r', 'n', 'ng', 'ny']
    
    for base in base_prefixes:
        if prefix.startswith(base) and len(prefix) > len(base):
            potential_infix = prefix[len(base):]
            if potential_infix in infixes:
                return (base, potential_infix)
    
    return (prefix, '')
```

**Contoh**:
```
pembelajaran:
  prefix: "pem" → base: "pe", infix: "m"
  
membaca:
  prefix: "me" → base: "me", infix: ""
  root: "mbaca" → infix: "m" (extracted), root: "baca"
```

### 5.3 Lemmatization dengan nlp-id

Menggunakan library `nlp-id` untuk mendapatkan root word yang akurat:

```python
from nlp_id.lemmatizer import Lemmatizer

lemmatizer = Lemmatizer()

# Contoh
word = "pembelajaran"
lemma = lemmatizer.lemmatize(word)  # → "ajar"

# Dengan analisis morfologi
prefix, detected_root, suffix, lemma = analyze_with_lemmatizer(word)
# prefix: "pe"
# detected_root: "mbelajar" (dengan infix)
# suffix: "an"
# lemma: "ajar" (root murni)
```

---

## 6. Spell Checker

### 6.1 Pattern-Based Detection

Spell checker menggunakan pattern matching untuk mendeteksi typo:

#### **Pattern 1: Terlalu Banyak Konsonan**
```python
pattern = r'[bcdfghjklmnpqrstvwxyz]{5,}'
# Deteksi 5+ konsonan berurutan

Contoh:
- "pmbljrn" ✗ (7 konsonan berurutan)
- "pembelajaran" ✓
```

#### **Pattern 2: Karakter Berulang**
```python
pattern = r'(.)\1{2,}'
# Deteksi karakter sama 3+ kali

Contoh:
- "mmmembaca" ✗ (m berulang 3x)
- "membaca" ✓
```

#### **Pattern 3: Tidak Ada Vokal**
```python
pattern = r'^[bcdfghjklmnpqrstvwxyz]+$'
# Kata tanpa vokal (kecuali sangat pendek)

Contoh:
- "bljr" ✗ (tidak ada vokal)
- "belajar" ✓
```

### 6.2 Suggestion Algorithm

```python
def get_suggestions(word):
    """
    Generate suggestions menggunakan common replacements
    """
    common_replacements = {
        'i': ['y', 'e'],
        'y': ['i'],
        'e': ['i', 'a'],
        'a': ['e'],
        'u': ['o'],
        'o': ['u'],
        'k': ['c', 'q'],
        'c': ['k'],
        's': ['z'],
        'z': ['s']
    }
    
    suggestions = []
    for i, char in enumerate(word):
        if char in common_replacements:
            for replacement in common_replacements[char]:
                suggestion = word[:i] + replacement + word[i+1:]
                suggestions.append(suggestion)
    
    return suggestions[:5]  # Return top 5
```

### 6.3 Workflow

```
User Input → Check Patterns → Typo Detected? 
                                    ↓
                            Yes ←───┴───→ No
                             ↓              ↓
                    Show Warning      Process Text
                             ↓
                    User Decision
                    ↓         ↓
              Fix Typo   Proceed Anyway
```

---

## 7. API Endpoints

### 7.1 POST `/split`

**Deskripsi**: Memisahkan teks menjadi suku kata

**Request**:
```json
{
  "text": "pembelajaran Indonesia",
  "method": "kbbi"  // atau "puebi"
}
```

**Response**:
```json
{
  "results": [
    {
      "word": "pembelajaran",
      "syllables": ["pe", "m", "bel", "a", "jar", "an"]
    },
    {
      "word": "Indonesia",
      "syllables": ["In", "do", "ne", "si", "a"]
    }
  ],
  "method": "kbbi"
}
```

**Error Response**:
```json
{
  "error": "No text provided"
}
```

### 7.2 POST `/check_spelling`

**Deskripsi**: Mengecek typo dalam teks

**Request**:
```json
{
  "text": "pmbljrn mngrjkn"
}
```

**Response**:
```json
{
  "has_typos": true,
  "typos": [
    {
      "word": "pmbljrn",
      "is_correct": false,
      "reason": "Terlalu banyak konsonan berurutan",
      "suggestions": []
    },
    {
      "word": "mngrjkn",
      "is_correct": false,
      "reason": "Terlalu banyak konsonan berurutan",
      "suggestions": ["mngrjcn", "mngrjqn"]
    }
  ]
}
```

### 7.3 GET `/`

**Deskripsi**: Render halaman utama aplikasi

**Response**: HTML page

---

## 8. Teknologi dan Dependencies

### 8.1 Backend Stack

#### **Python 3.12+**
- Language runtime

#### **Flask 3.0.0**
- Web framework
- Routing
- Template rendering
- JSON API

#### **nlp-id 0.1.20.0**
- Indonesian NLP library
- Lemmatization
- Root word detection
- Morphological analysis

#### **pyspellchecker 0.8.4**
- Spell checking base library
- Edit distance calculation
- Word frequency (customized for Indonesian)

### 8.2 Frontend Stack

#### **HTML5**
- Semantic structure
- Form handling
- SVG icons

#### **CSS3**
- Glassmorphism design
- Dark theme
- Animations
- Responsive layout

#### **Vanilla JavaScript**
- AJAX requests (Fetch API)
- DOM manipulation
- Event handling
- Clipboard API

#### **Google Fonts**
- Inter font family
- Modern typography

### 8.3 Dependencies Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# atau
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

**requirements.txt**:
```
Flask==3.0.0
nlp-id==0.1.20.0
pyspellchecker==0.8.4
```

### 8.4 Running the Application

```bash
# Development mode
python app.py

# Server runs on http://127.0.0.1:5000
# Debug mode: ON
# Auto-reload: ON
```

**Production mode**:
```python
# Modify app.py
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

---

## 9. Exception Dictionary

### 9.1 Format

File: `exceptions.json`

```json
{
  "kata": ["suku", "kata", "hasil"],
  "belajar": ["bel", "a", "jar"],
  "pelajar": ["pel", "a", "jar"],
  "ajar": ["a", "jar"],
  "bangun": ["ba", "ngun"],
  "tangan": ["ta", "ngan"]
}
```

### 9.2 Penggunaan

Exception dictionary digunakan untuk:
1. **Kata-kata yang tidak mengikuti aturan umum**
2. **Kata-kata dengan pemisahan khusus di KBBI**
3. **Meningkatkan akurasi untuk kata-kata kompleks**

### 9.3 Priority

```
Exception Check → Morphological Analysis → Syllable Rules
     (highest)              (medium)           (lowest)
```

---

## 10. Testing dan Validasi

### 10.1 Test Cases

#### **PUEBI Method**:
```
Input          → Expected Output
pembelajaran   → pem-be-la-ja-ran
Indonesia      → In-do-ne-si-a
komputer       → kom-pu-ter
bangunan       → ba-ngu-nan
membaca        → mem-ba-ca
banyak         → ba-nyak
```

#### **KBBI Method**:
```
Input          → Expected Output
pembelajaran   → pe-m-bel-a-jar-an
Indonesia      → In-do-ne-si-a
komputer       → kom-pu-ter
bangunan       → ba-ngun
membaca        → me-m-ba-ca
banyak         → ba-nyak
```

### 10.2 Testing via Browser

1. Buka `http://127.0.0.1:5000`
2. Pilih metode (PUEBI/KBBI)
3. Input kata test
4. Verifikasi hasil

### 10.3 Testing via curl

```bash
# Syllable splitting
curl -X POST http://127.0.0.1:5000/split \
  -H "Content-Type: application/json" \
  -d '{"text": "pembelajaran", "method": "kbbi"}'

# Spell checking
curl -X POST http://127.0.0.1:5000/check_spelling \
  -H "Content-Type: application/json" \
  -d '{"text": "pmbljrn"}'
```

---

## 11. Referensi

### 11.1 Dokumen Resmi

1. **PUEBI** (Pedoman Umum Ejaan Bahasa Indonesia)
   - URL: https://repositori.kemendikdasmen.go.id/270/1/PUEBI.pdf
   - Sumber: Kementerian Pendidikan dan Kebudayaan

2. **KBBI Online**
   - URL: https://kbbi.kemdikbud.go.id/
   - Sumber: Badan Pengembangan dan Pembinaan Bahasa

### 11.2 Library dan Tools

1. **syllable_splitter** (Original)
   - GitHub: https://github.com/fahadh4ilyas/syllable_splitter
   - Author: fahadh4ilyas
   - License: MIT

2. **nlp-id**
   - GitHub: https://github.com/ir-nlp-csui/nlp-id
   - Author: Kumparan NLP Team
   - Purpose: Indonesian NLP tools

3. **pyspellchecker**
   - GitHub: https://github.com/barrust/pyspellchecker
   - Author: barrust
   - Purpose: Spell checking library

### 11.3 Academic References

1. **Pemenggalan Kata dalam Bahasa Indonesia**
   - Sumber: Pusat Bahasa Kemendikbud
   - Topik: Aturan syllabification

2. **Morfologi Bahasa Indonesia**
   - Topik: Prefix, suffix, infix, circumfix
   - Aplikasi: Morphological analysis

---

## 12. Kesimpulan

### 12.1 Keunggulan Sistem

1. **Dua Metode Berbeda**
   - PUEBI: Aturan resmi, sederhana, konsisten
   - KBBI: Morfologi-aware, lebih akurat untuk kata berimbuhan

2. **Spell Checker Terintegrasi**
   - Pattern-based detection
   - User-friendly warnings
   - Suggestion system

3. **Modern Web Interface**
   - Responsive design
   - Real-time processing
   - Smooth animations

4. **Extensible Architecture**
   - Exception dictionary
   - Modular components
   - Clear separation of concerns

### 12.2 Limitasi

1. **Exception Dictionary**
   - Memerlukan maintenance manual
   - Belum lengkap untuk semua kata khusus

2. **Spell Checker**
   - Pattern-based (bukan dictionary-based)
   - Suggestions terbatas

3. **Morphological Analysis**
   - Bergantung pada nlp-id lemmatizer
   - Tidak 100% akurat untuk kata sangat kompleks

### 12.3 Future Improvements

1. **Expand Exception Dictionary**
   - Tambah lebih banyak kata khusus
   - Crowdsourcing dari pengguna

2. **Enhanced Spell Checker**
   - Indonesian word frequency database
   - Machine learning-based suggestions

3. **API Enhancements**
   - Batch processing
   - Rate limiting
   - Authentication

4. **UI/UX Improvements**
   - History tracking
   - Export results (PDF, CSV)
   - Comparison view (PUEBI vs KBBI side-by-side)

---

**Dokumen ini dibuat untuk keperluan presentasi akademik**  
**Syllable Splitter - Pemisah Suku Kata Bahasa Indonesia**  
**© 2024 - Based on syllable_splitter by fahadh4ilyas**
