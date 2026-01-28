# 📚 Indonesian Syllable Splitter - Complete Documentation

**Aplikasi pemisah suku kata bahasa Indonesia dengan 3 metode berbeda dan deteksi typo otomatis**

---

## 📖 Tentang Aplikasi

Aplikasi ini adalah **web-based tool** yang dapat memisahkan kata bahasa Indonesia menjadi suku-suku kata menggunakan berbagai metode, lengkap dengan:
- ✅ **3 Metode Pemisahan**: PUEBI, SylBI, dan KBBI Online
- ✅ **Deteksi Typo Otomatis**: Validasi dengan 112,643 kata dari KBBI
- ✅ **Deteksi Bahasa**: Identifikasi kata non-Indonesia
- ✅ **Analisis Morfologi**: Pemisahan awalan, sisipan, kata dasar, dan akhiran
- ✅ **CLI Support**: Dapat dijalankan via command line

**Contoh:**
- `pembelajaran` → `pe-m-be-l-a-jar-an` (SylBI)
- `Indonesia` → `In-do-ne-si-a`
- `computer` → ⚠️ Terdeteksi bahasa Inggris

---

## 🎯 Tiga Metode Pemisahan

### 1. **PUEBI** (Pedoman Umum Ejaan Bahasa Indonesia)
Metode resmi dari Kemendikbud berdasarkan aturan pemenggalan kata PUEBI.

**Karakteristik:**
- Pemisahan suku kata murni tanpa analisis morfologi
- Mengikuti aturan fonetik bahasa Indonesia
- Cocok untuk keperluan ejaan umum

**Contoh:**
```
pembelajaran  → pem-be-la-ja-ran
membaca       → mem-ba-ca
Indonesia     → In-do-ne-si-a
```

---

### 2. **SylBI** (Syllabification for Bahasa Indonesia)
Metode hybrid yang menggabungkan analisis morfologi dengan pemisahan suku kata.

**Karakteristik:**
- Memisahkan awalan (prefix), sisipan (infix), kata dasar (root), dan akhiran (suffix)
- Menangani peluluhan (nasal assimilation)
- Menangani awalan bertingkat (nested prefixes)
- Cocok untuk analisis linguistik dan riset

**Contoh:**
```
pembelajaran  → pe-m-be-l-a-jar-an
                (pe + m + be + l + ajar + an)
                
membaca       → me-m-ba-ca
                (me + m + baca)
                
mengetik      → me-ng-ke-tik
                (me + ng + ketik)
```

#### **Cara Kerja SylBI:**

##### **Langkah 1: Analisis Morfologi**
Menggunakan lemmatizer dari `nlp-id` untuk mendeteksi:
- **Prefix** (awalan): me-, ber-, pe-, ter-, di-, ke-, se-
- **Root** (kata dasar): kata asli tanpa imbuhan
- **Suffix** (akhiran): -kan, -an, -i, -nya, -ku, -mu

##### **Langkah 2: Dekomposisi Prefix**
Memisahkan prefix menjadi **base prefix** dan **infix** (sisipan):

| Prefix | Base | Infix | Contoh |
|--------|------|-------|--------|
| `pem` | `pe` | `m` | **pem**baca → pe + m + baca |
| `pel` | `pe` | `l` | **pel**ajar → pe + l + ajar |
| `bel` | `be` | `l` | **bel**ajar → be + l + ajar |
| `peng` | `pe` | `ng` | **peng**ecualian → pe + ng + kecualian |
| `peny` | `pe` | `ny` | **peny**apu → pe + ny + sapu |

##### **Langkah 3: Penanganan Peluluhan (Nasal Assimilation)**
Ketika prefix nasal bertemu dengan kata dasar yang dimulai konsonan tertentu, konsonan tersebut **luluh** (hilang). SylBI mengembalikan konsonan asli untuk pemisahan yang akurat.

**Aturan Peluluhan:**

| Infix | Konsonan Luluh | Contoh | Hasil |
|-------|----------------|--------|-------|
| `m` | `p` | me**m**isah (← **p**isah) | me-m-**pi**-sah |
| `m` | `p` | me**m**akai (← **p**akai) | me-m-**pa**-kai |
| `n` | `t` | me**n**ari (← **t**ari) | me-n-**ta**-ri |
| `n` | `t` | pe**n**urunan (← **t**urun) | pe-n-**tu**-run-an |
| `ng` | `k` | me**ng**etik (← **k**etik) | me-ng-**ke**-tik |
| `ny` | `s` | me**ny**apu (← **s**apu) | me-ny-**sa**-pu |

**Algoritma Peluluhan:**
1. Deteksi infix dari prefix (m, n, ng, ny)
2. Gunakan lemmatizer untuk mendapatkan kata dasar asli
3. Jika kata dasar dimulai dengan p/t/k/s, kembalikan konsonan tersebut
4. Pisahkan: prefix + infix + **konsonan** + sisa kata

**Contoh Detail:**

**memisah** (kata dasar: **pisah**):
```
Input:  memisah
Prefix: me
Infix:  m (dari pem-)
Root:   pisah (lemmatizer mengembalikan "pisah")
Proses: Konsonan 'p' dikembalikan karena infix 'm' → peluluhan dari 'p'
Output: me-m-pi-sah ✅
```

**memakai** (kata dasar: **pakai**):
```
Input:  memakai
Prefix: me
Infix:  m (dari pem-)
Root:   pakai (lemmatizer mengembalikan "pakai")
Proses: Konsonan 'p' dikembalikan karena infix 'm' → peluluhan dari 'p'
Output: me-m-pa-kai ✅
```

**mengetik** (kata dasar: **ketik**):
```
Input:  mengetik
Prefix: me
Infix:  ng (dari peng-)
Root:   ketik (lemmatizer mengembalikan "ketik")
Proses: Konsonan 'k' dikembalikan karena infix 'ng' → peluluhan dari 'k'
Output: me-ng-ke-tik ✅
```

**mengemban** (kata dasar: **emban**):
```
Input:  mengemban
Prefix: me
Infix:  ng (dari peng-)
Root:   emban (lemmatizer mengembalikan "emban")
Proses: TIDAK ada peluluhan (kata dasar dimulai dengan vokal 'e')
Output: me-ng-em-ban ✅
```

##### **Langkah 4: Penanganan Awalan Bertingkat (Nested Prefixes)**
Kata dapat memiliki lebih dari satu prefix dengan infix masing-masing.

**Contoh: pembelajaran**
```
Input:  pembelajaran
Analisis:
  - Prefix 1: pe + m (pem-)
  - Prefix 2: be + l (bel-)
  - Root:     ajar
  - Suffix:   an
  
Output: pe-m-be-l-a-jar-an ✅
```

**Algoritma:**
1. Ekstrak prefix pertama dan infixnya
2. Cek apakah sisa kata dimulai dengan prefix lain
3. Jika ya, ekstrak prefix kedua dan infixnya
4. Ulangi sampai tidak ada prefix lagi
5. Sisanya adalah root + suffix

##### **Langkah 5: Pemisahan Suku Kata**
Setelah morfologi teridentifikasi, setiap bagian dipisahkan menjadi suku kata:
- **Prefix & Infix**: Dipisahkan sebagai suku kata individual
- **Root**: Dipisahkan menggunakan aturan KBBI
- **Suffix**: Biasanya tetap satu suku (kecuali >3 huruf)

---

### 3. **KBBI Scraper** (Online Dictionary)
Mengambil pemisahan suku kata langsung dari KBBI Online (kbbi.kemdikbud.go.id).

**Karakteristik:**
- Data langsung dari sumber resmi
- Memerlukan koneksi internet
- Fallback ke PUEBI jika kata tidak ditemukan

**Contoh:**
```
pembelajaran  → pem-bel-a-jar-an (sesuai KBBI)
membaca       → mem-ba-ca
```

---

## ✅ Deteksi Typo & Validasi KBBI

### **Fitur Spell Checking**

Aplikasi menggunakan **112,643 kata dari KBBI** untuk validasi dan memberikan 3 jenis peringatan:

#### **1. 🔴 Kemungkinan Typo**
Deteksi pola salah eja:
- **Konsonan berlebihan**: 5+ konsonan berurutan
  - `pmbljrn` ❌ → Saran: `pembelajaran`
- **Karakter berulang**: 3+ karakter sama berurutan
  - `mmmembaca` ❌ → Saran: `membaca`
- **Tidak ada vokal**: Kata panjang tanpa a/i/u/e/o
  - `bljr` ❌ → Saran: `belajar`

#### **2. 🟡 Tidak Ditemukan di KBBI**
Kata tidak ada dalam database KBBI:
```
komputr ❌ → Saran: komputer, komputasi
Indonsia ❌ → Saran: Indonesia
```

**Algoritma Suggestions:**
- Menggunakan **edit distance** (SequenceMatcher)
- Mencari kata dengan similarity >70%
- Mempertimbangkan panjang kata (±2 karakter)
- Menampilkan top 5 suggestions

#### **3. 🔵 Bukan Bahasa Indonesia**
Deteksi kata asing:

**Common English Words:**
```
computer, learning, hello, world → Terdeteksi bahasa Inggris
```

**English Patterns:**
```
-tion  → education, information
-ing   → learning, teaching
th-    → the, this, that
-ght   → night, light
```

**Huruf Jarang:**
```
q, x, f → question, example, coffee
(kecuali kata serapan yang ada di KBBI)
```

### **Penggunaan di Web Interface**

Ketika spell check diaktifkan:
1. User mengetik teks
2. Klik "Pisahkan Suku Kata"
3. **SweetAlert popup** muncul jika ada error
4. User dapat:
   - **Lanjutkan Tetap**: Proses meskipun ada error
   - **Perbaiki Dulu**: Kembali edit teks

### **Penggunaan di CLI**

```bash
# Dengan spell check (default)
python3 HybridSyllableSplitter.py "computer learning"

# Output:
⚠️  PERINGATAN DETEKSI KATA:
============================================================

🔵 Bukan Bahasa Indonesia:
  • computer - Terdeteksi sebagai kata bahasa Inggris
  • learning - Akhiran bahasa Inggris (-ing)

============================================================
Lanjutkan pemisahan suku kata? (y/n):

# Skip spell check
python3 HybridSyllableSplitter.py "membaca" --no-spell-check
```

---

## 📏 Aturan PUEBI (Detail)

Pemisahan suku kata murni mengikuti aturan fonetik bahasa Indonesia berdasarkan **Pedoman Umum Ejaan Bahasa Indonesia (PUEBI)**.

### **1. Pemenggalan Kata Dasar**

#### **a. Vokal Berurutan (VV)**
Jika di tengah kata terdapat huruf vokal yang berurutan, pemenggalannya dilakukan di antara kedua huruf vokal itu.
- `buah` → `bu-ah`
- `main` → `ma-in`
- `niat` → `ni-at`
- `saat` → `sa-at`

#### **b. Diftong**
Huruf diftong **ai, au, ei, dan oi** tidak dipenggal.
- `pandai` → `pan-dai`
- `aula` → `au-la`
- `saudara` → `sau-da-ra`
- `survei` → `sur-vei`
- `amboi` → `am-boi`

#### **c. Vokal-Konsonan-Vokal (VKV)**
Jika di tengah kata dasar terdapat huruf konsonan (termasuk gabungan huruf konsonan) di antara dua huruf vokal, pemenggalannya dilakukan sebelum huruf konsonan itu.
- `bapak` → `ba-pak`
- `lawan` → `la-wan`
- `dengan` → `de-ngan`
- `kenyang` → `ke-nyang`
- `mutakhir` → `mu-ta-khir`
- `musyawarah` → `mu-sya-wa-rah`

#### **d. Dua Konsonan Berurutan (VKKV)**
Jika di tengah kata dasar terdapat dua huruf konsonan yang berurutan, pemenggalannya dilakukan di antara kedua huruf konsonan itu.
**Catatan:** Gabungan huruf konsonan yang melambangkan satu bunyi tidak dipenggal.
- `April` → `Ap-ril`
- `caplok` → `cap-lok`
- `makh-luk` → `makh-luk`
- `mandi` → `man-di`
- `sanggup` → `sang-gup`
- `sombong` → `som-bong`
- `swasta` → `swas-ta`
- `bangsa` → `bang-sa` (cluster)
- `banyak` → `ba-nyak` (cluster)

#### **e. Tiga Konsonan Berurutan atau Lebih (VKKKV)**
Jika di tengah kata dasar terdapat tiga huruf konsonan atau lebih yang masing-masing melambangkan satu bunyi, pemenggalannya dilakukan di antara huruf konsonan yang pertama dan huruf konsonan yang kedua.
- `ultra` → `ul-tra`
- `infra` → `in-fra`
- `bentrok` → `ben-trok`
- `instrumen` → `in-stru-men`
- `bang-krut` → `bang-krut` (cluster `ng` tidak dipenggal)

---

### **2. Pemenggalan Kata Turunan**

Pemenggalan kata turunan sedapat-dapatnya dilakukan di antara bentuk dasar dan unsur pembentuknya.
- `ber-jalan`
- `mem-bantu`
- `di-ambil`
- `ter-bawa`
- `makan-an`
- `letak-kan`
- `pergi-lah`
- `apa-kah`

**Catatan Khusus:**
1. **Apitan atau Luluhan (Simulfiks)**: Pemenggalan kata berimbuhan yang bentuk dasarnya mengalami perubahan dilakukan seperti pada kata dasar.
   - `me-nu-tup` (dari tutup)
   - `me-ma-kai` (dari pakai)
   - `pe-mi-kir` (dari pikir)
2. **Sisipan (Infiks)**: Pemenggalan kata bersisipan dilakukan seperti pada kata dasar.
   - `ge-lem-bung` (sisipan -el-)
   - `ge-mu-ruh` (sisipan -em-)
   - `si-nam-bung` (sisipan -in-)
   - `te-lun-juk` (sisipan -el-)

---

### **3. Unsur Gabungan**
Jika sebuah kata terdiri atas dua unsur atau lebih dan salah satu unsurnya itu dapat bergabung dengan unsur lain, pemenggalannya dilakukan di antara unsur-unsur itu. Tiap unsur gabungan itu dipenggal seperti pada kata dasar.
- `biografi` → `bio-grafi` → `bi-o-gra-fi`
- `biodata` → `bio-data` → `bi-o-da-ta`
- `pascapanen` → `pasca-panen` → `pas-ca-pa-nen`
- `kilometer` → `kilo-meter` → `ki-lo-me-ter`

---

## 🛠️ Teknologi & Arsitektur

### **Backend**
- **Python 3.12**
- **Flask 3.0.0** - Web framework
- **nlp-id** - Indonesian NLP library (lemmatizer)
- **pandas** - KBBI CSV processing
- **BeautifulSoup4** - KBBI web scraping
- **difflib** - Edit distance untuk suggestions

### **Frontend**
- **HTML5** + **CSS3** + **JavaScript**
- **SweetAlert2** - Beautiful alert dialogs
- **Google Fonts (Inter)** - Modern typography
- **Responsive Design** - Mobile-friendly

### **Data**
- **kbbi_v.csv** - 112,643 kata dari KBBI
- **exceptions.json** - Kata-kata dengan aturan khusus

---

## 📁 Struktur File

```
📁 Syllable Splitter/
├── 🐍 app.py                          # Flask application
├── 📄 requirements.txt                # Python dependencies
├── 📄 rules.md                        # Dokumentasi ini
│
├── 📁 Core Modules/
│   ├── PUEBIOfficialSplitter.py      # PUEBI method
│   ├── HybridSyllableSplitter.py     # SylBI method
│   ├── KBBISyllableSplitter.py       # KBBI syllable rules
│   ├── KBBIScraper.py                # KBBI online scraper
│   ├── MorphologicalAnalyzer.py      # Morphology analysis
│   ├── SpellChecker.py               # Spell checking + KBBI validation
│   └── exceptions.json               # Exception dictionary
│
├── 📁 templates/
│   └── index.html                    # Web interface
│
├── 📁 static/
│   └── style.css                     # Styling
│
└── 📊 kbbi_v.csv                      # KBBI word database (112,643 words)
```

---

## 🚀 Cara Menggunakan

### **1. Web Interface**

#### **Setup:**
```bash
# Clone repository
git clone <repository-url>
cd "Syllable Splitter"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# atau
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python3 app.py
```

#### **Akses:**
Buka browser: `http://localhost:5000`

#### **Fitur Web:**
- ✅ Input teks (single/multiple words)
- ✅ Pilih metode (PUEBI/SylBI/KBBI)
- ✅ Toggle spell check
- ✅ SweetAlert warnings
- ✅ Copy hasil ke clipboard
- ✅ Contoh cepat (quick examples)

---

### **2. Command Line Interface**

#### **HybridSyllableSplitter (SylBI):**
```bash
# Basic usage
python3 HybridSyllableSplitter.py "pembelajaran"
# Output: pe-m-be-l-a-jar-an

# With verbose (show morphology)
python3 HybridSyllableSplitter.py "pembelajaran" --verbose
# Output:
# Morphology: prefix='pem', root='belajar', suffix='an'
# Result: ['pe', 'm', 'be', 'l', 'a', 'jar', 'an']
# Joined: pe-m-be-l-a-jar-an

# Skip spell check
python3 HybridSyllableSplitter.py "membaca" --no-spell-check
```

#### **PUEBIOfficialSplitter (PUEBI):**
```bash
python3 PUEBIOfficialSplitter.py "pembelajaran"
# Output: pem-be-la-ja-ran

python3 PUEBIOfficialSplitter.py "computer" --no-spell-check
```

#### **KBBIScraper (KBBI Online):**
```bash
python3 KBBIScraper.py "pembelajaran"
# Output: pem-bel-a-jar-an (from KBBI online)
```

---

## 🔌 API Endpoints

### **1. POST /split**
Memisahkan teks menjadi suku kata.

**Request:**
```json
{
  "text": "pembelajaran Indonesia",
  "method": "sylbi"
}
```

**Response:**
```json
{
  "results": [
    {
      "word": "pembelajaran",
      "syllables": ["pe", "m", "be", "l", "a", "jar", "an"]
    },
    {
      "word": "Indonesia",
      "syllables": ["In", "do", "ne", "si", "a"]
    }
  ],
  "method": "sylbi"
}
```

**Methods:** `puebi`, `sylbi`, `kbbi`

---

### **2. POST /check_spelling**
Memeriksa ejaan dan memberikan suggestions.

**Request:**
```json
{
  "text": "computer pmbljrn"
}
```

**Response:**
```json
{
  "has_typos": true,
  "typos": [
    {
      "word": "computer",
      "is_correct": false,
      "error_type": "non_indonesian",
      "reason": "Terdeteksi sebagai kata bahasa Inggris",
      "suggestions": []
    },
    {
      "word": "pmbljrn",
      "is_correct": false,
      "error_type": "typo",
      "reason": "Terlalu banyak konsonan berurutan",
      "suggestions": ["pembelajaran", "pembela"]
    }
  ]
}
```

**Error Types:**
- `typo` - Pola salah eja
- `not_found` - Tidak ada di KBBI
- `non_indonesian` - Bukan bahasa Indonesia

---

## 🧪 Testing Examples

### **Test SylBI (Morphological Analysis)**

```bash
# Basic words
pembelajaran  → pe-m-be-l-a-jar-an
membaca       → me-m-ba-ca
Indonesia     → In-do-ne-si-a

# Nasal assimilation (peluluhan)
memisah       → me-m-pi-sah      # m + pisah
memakai       → me-m-pa-kai      # m + pakai
mengetik      → me-ng-ke-tik     # ng + ketik
menyapu       → me-ny-sa-pu      # ny + sapu
penurunan     → pe-n-tu-run-an   # n + turun

# No assimilation (root starts with vowel)
mengemban     → me-ng-em-ban     # ng + emban (no 'k')
mengajar      → me-ng-a-jar      # ng + ajar (no 'k')

# Nested prefixes
pembelajaran  → pe-m-be-l-a-jar-an  # (pe+m) + (be+l) + ajar + an

# Two-character infixes
pengecualian  → pe-ng-ke-cu-a-li-an  # pe + ng + kecualian
penyapu       → pe-ny-sa-pu          # pe + ny + sapu
```

### **Test PUEBI (Phonetic Rules)**

```bash
pembelajaran  → pem-be-la-ja-ran
membaca       → mem-ba-ca
banyak        → ba-nyak
saudara       → sau-da-ra
instrumen     → in-stru-men
```

### **Test Spell Checking**

```bash
# Valid Indonesian
python3 HybridSyllableSplitter.py "pembelajaran"
# ✓ No warnings

# Typo
python3 HybridSyllableSplitter.py "pmbljrn"
# 🔴 Typo: Terlalu banyak konsonan berurutan

# Non-Indonesian
python3 HybridSyllableSplitter.py "computer learning"
# 🔵 Non-Indonesian: Terdeteksi bahasa Inggris

# Not in KBBI
python3 HybridSyllableSplitter.py "komputr"
# 🟡 Not Found: Saran: komputer, komputasi
```

---

## 📚 Referensi

### **Dokumen Resmi**
1. **PUEBI** - Pedoman Umum Ejaan Bahasa Indonesia
   - Sumber: Kemendikbud
   - Link: https://repositori.kemendikdasmen.go.id/270/1/PUEBI.pdf

2. **KBBI Online**
   - Sumber: Badan Pengembangan dan Pembinaan Bahasa
   - Link: https://kbbi.kemdikbud.go.id/

### **Libraries**
1. **nlp-id** - Indonesian NLP tools
   - GitHub: https://github.com/ir-nlp-csui/nlp-id
2. **SweetAlert2** - Beautiful alerts
   - Website: https://sweetalert2.github.io/

---

## 💡 Perbandingan Metode

| Aspek | PUEBI | SylBI | KBBI Scraper |
|-------|-------|-------|--------------|
| **Fokus** | Fonetik | Morfologi + Fonetik | Referensi Resmi |
| **Analisis Imbuhan** | ❌ | ✅ | ❌ |
| **Peluluhan** | ❌ | ✅ | ❌ |
| **Nested Prefix** | ❌ | ✅ | ❌ |
| **Internet** | ❌ | ❌ | ✅ |
| **Kecepatan** | ⚡⚡⚡ | ⚡⚡ | ⚡ |
| **Akurasi** | Tinggi | Sangat Tinggi | Referensi |
| **Use Case** | Ejaan umum | Riset linguistik | Validasi KBBI |

### **Kapan Menggunakan?**

**PUEBI:**
- ✅ Keperluan ejaan umum
- ✅ Pemisahan suku kata sederhana
- ✅ Tidak butuh analisis morfologi

**SylBI:**
- ✅ Analisis linguistik
- ✅ Riset morfologi bahasa Indonesia
- ✅ Butuh detail awalan, sisipan, kata dasar, akhiran
- ✅ Studi peluluhan dan imbuhan

**KBBI Scraper:**
- ✅ Validasi dengan sumber resmi
- ✅ Cross-check hasil
- ✅ Ada koneksi internet

---

## 🎓 Untuk Peneliti & Developer

### **Extending the System**

#### **Menambah Kata Exception:**
Edit `exceptions.json`:
```json
{
  "kata_khusus": ["ka", "ta", "khu", "sus"],
  "contoh": ["con", "toh"]
}
```

#### **Custom Spell Checker:**
Extend `SpellChecker.py`:
```python
class CustomSpellChecker(IndonesianSpellChecker):
    def __init__(self):
        super().__init__()
        # Add custom words
        self.kbbi_words.update(['kata1', 'kata2'])
```

#### **API Integration:**
```python
import requests

response = requests.post('http://localhost:5000/split', json={
    'text': 'pembelajaran',
    'method': 'sylbi'
})

result = response.json()
print(result['results'][0]['syllables'])
# Output: ['pe', 'm', 'be', 'l', 'a', 'jar', 'an']
```

---

## 📄 Lisensi

MIT License - Silakan digunakan untuk keperluan akademis dan komersial.

---

## 👥 Kontribusi

Kontribusi sangat diterima! Silakan:
1. Fork repository
2. Buat branch fitur baru
3. Submit pull request

---

## 📞 Kontak & Support

Untuk pertanyaan, bug reports, atau feature requests, silakan buka issue di GitHub repository.

---

**Selamat menggunakan Indonesian Syllable Splitter! 🎉**

*Dokumentasi ini dibuat untuk memudahkan pemahaman dan penggunaan aplikasi, baik untuk pengguna umum maupun peneliti linguistik.*
