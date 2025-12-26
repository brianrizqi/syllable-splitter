# 🔤 Syllable Splitter - Pemisah Suku Kata Bahasa Indonesia

Aplikasi web untuk memisahkan kata menjadi suku kata dalam bahasa Indonesia dengan dua metode: **PUEBI** (Pedoman Umum Ejaan Bahasa Indonesia) dan **KBBI** (Kamus Besar Bahasa Indonesia).

## ✨ Fitur Utama

- ✅ **Dua Metode Pemisahan**
  - **PUEBI**: Menggunakan aturan resmi PUEBI
  - **KBBI**: Hybrid morfologi + syllable dengan nlp-id Lemmatizer
- ✅ **Spell Checker**: Deteksi typo sebelum memproses
- ✅ **Analisis Morfologi**: Deteksi prefix, suffix, infix, dan root word
- ✅ **Exception Dictionary**: Database kata-kata khusus untuk akurasi maksimal
- ✅ **Desain Modern**: Dark theme dengan glassmorphism dan animasi smooth
- ✅ **Responsive**: Berfungsi di HP, tablet, dan desktop
- ✅ **Real-time Processing**: AJAX tanpa reload halaman

## 🚀 Quick Start

### 1. Clone atau Download Repository

```bash
cd "Syllable Splitter"
```

### 2. Buat Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # Di Mac/Linux
# atau
venv\Scripts\activate  # Di Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies yang akan diinstall:
- `Flask==3.0.0` - Web framework
- `nlp-id==0.1.20.0` - Indonesian NLP library untuk lemmatization
- `pyspellchecker==0.8.4` - Spell checking library

### 4. Jalankan Aplikasi

```bash
python app.py
```

Server akan berjalan di: **http://127.0.0.1:5000**

### 5. Buka di Browser

```
http://127.0.0.1:5000
```

## 📖 Cara Menggunakan

1. **Pilih Metode**: PUEBI atau KBBI
2. **Aktifkan Spell Checker** (opsional): Centang "Cek Ejaan Sebelum Memproses"
3. **Masukkan Teks**: Ketik kata atau kalimat di kotak input
4. **Proses**: Klik "Pisahkan Suku Kata" atau tekan Enter
5. **Lihat Hasil**: Hasil pemisahan akan muncul dengan animasi
6. **Salin**: Klik tombol "Salin" untuk copy hasil

### Contoh Hasil

**Input**: `pembelajaran`

**PUEBI**: `pem + be + la + ja + ran`

**KBBI**: `pe + m + bel + a + jar + an`
- Prefix: `pe-`
- Infix: `-m-`
- Root: `belajar` (dengan exception splitting: `bel-a-jar`)
- Suffix: `-an`

## 🔧 Teknologi

### Backend
- **Python 3.12+**
- **Flask 3.0.0** - Web framework
- **nlp-id 0.1.20.0** - Indonesian lemmatizer untuk root word detection
- **pyspellchecker 0.8.4** - Spell checking

### Frontend
- **HTML5** - Struktur
- **CSS3** - Styling dengan glassmorphism
- **Vanilla JavaScript** - Interaktivitas
- **Google Fonts (Inter)** - Typography

### Algoritma
- **PUEBIOfficialSplitter** - Implementasi aturan PUEBI
- **HybridSyllableSplitter** - Kombinasi morfologi + syllable
- **MorphologicalAnalyzer** - Analisis prefix, suffix, infix dengan nlp-id
- **IndonesianSpellChecker** - Pattern-based typo detection

## 📁 Struktur Proyek

```
Syllable Splitter/
├── app.py                      # Flask application
├── requirements.txt            # Python dependencies
│
├── Core Modules/
│   ├── PUEBIOfficialSplitter.py    # PUEBI method
│   ├── HybridSyllableSplitter.py   # KBBI method
│   ├── MorphologicalAnalyzer.py    # Morphological analysis
│   ├── SpellChecker.py             # Typo detection
│   ├── KBBISyllableSplitter.py     # KBBI syllable rules
│   └── exceptions.json             # Exception dictionary
│
├── templates/
│   └── index.html              # Main HTML template
│
└── static/
    └── style.css               # CSS styling
```

## 📝 API Endpoints

### POST `/split`

Memisahkan teks menjadi suku kata.

**Request:**
```json
{
  "text": "pembelajaran Indonesia",
  "method": "kbbi"  // atau "puebi"
}
```

**Response:**
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

### POST `/check_spelling`

Mengecek typo dalam teks.

**Request:**
```json
{
  "text": "pmbljrn mngrjkn"
}
```

**Response:**
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

## 🎯 Perbedaan PUEBI vs KBBI

### PUEBI (Pedoman Umum Ejaan Bahasa Indonesia)
- Mengikuti aturan resmi PUEBI
- Pemisahan berdasarkan pola konsonan-vokal
- Tidak mempertimbangkan morfologi
- Contoh: `pembelajaran` → `pem-be-la-ja-ran`

### KBBI (Kamus Besar Bahasa Indonesia)
- Menggunakan analisis morfologi
- Deteksi prefix, suffix, infix dengan nlp-id Lemmatizer
- Exception dictionary untuk kata-kata khusus
- Lebih akurat untuk kata berimbuhan kompleks
- Contoh: `pembelajaran` → `pe-m-bel-a-jar-an`

## 🔍 Spell Checker

Spell checker menggunakan pattern matching untuk mendeteksi typo:

1. **Terlalu banyak konsonan**: 5+ konsonan berurutan
   - Contoh: `pmbljrn` ❌

2. **Karakter berulang**: Karakter sama 3+ kali
   - Contoh: `mmmembaca` ❌

3. **Tidak ada vokal**: Kata tanpa vokal (kecuali kata sangat pendek)
   - Contoh: `bljr` ❌

## 🛠️ Development

### Debug Mode

Server Flask berjalan dalam debug mode secara default untuk development:

```python
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Production Mode

Untuk production, ubah di `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

### Menambah Exception Words

Edit file `exceptions.json`:

```json
{
  "belajar": ["bel", "a", "jar"],
  "kata_baru": ["ka", "ta", "ba", "ru"]
}
```

## 🧪 Testing

### Test via Browser
1. Buka http://127.0.0.1:5000
2. Test dengan kata: `pembelajaran`, `pelajaran`, `membaca`
3. Bandingkan hasil PUEBI vs KBBI

### Test via curl

**Syllable Splitting:**
```bash
curl -X POST http://127.0.0.1:5000/split \
  -H "Content-Type: application/json" \
  -d '{"text": "pembelajaran", "method": "kbbi"}'
```

**Spell Checking:**
```bash
curl -X POST http://127.0.0.1:5000/check_spelling \
  -H "Content-Type: application/json" \
  -d '{"text": "pmbljrn"}'
```

## 📚 Referensi

- [PUEBI PDF](https://repositori.kemendikdasmen.go.id/270/1/PUEBI.pdf) - Pedoman Umum Ejaan Bahasa Indonesia
- [KBBI Online](https://kbbi.kemdikbud.go.id/) - Kamus Besar Bahasa Indonesia
- [syllable_splitter](https://github.com/fahadh4ilyas/syllable_splitter) - Original library by fahadh4ilyas
- [nlp-id](https://github.com/ir-nlp-csui/nlp-id) - Indonesian NLP library

## 🙏 Credits

- **Original Algorithm**: [fahadh4ilyas/syllable_splitter](https://github.com/fahadh4ilyas/syllable_splitter)
- **Indonesian NLP**: [Kumparan NLP Team](https://github.com/ir-nlp-csui/nlp-id)
- **Spell Checker**: [pyspellchecker](https://github.com/barrust/pyspellchecker)

## 📄 License

Based on the original syllable_splitter project.

---

**Selamat mencoba! 🎉**

Jika ada pertanyaan atau masalah, silakan buat issue atau hubungi developer.