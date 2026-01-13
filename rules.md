# 📚 Cara Kerja Aplikasi Pemisah Suku Kata

**Aplikasi untuk memisahkan kata bahasa Indonesia menjadi suku kata**

---

## 📖 Apa itu aplikasi ini?

Aplikasi ini adalah **website** yang bisa memisahkan kata bahasa Indonesia menjadi suku-suku kata.

**Contoh:**
- `pembelajaran` → `pe-m-be-l-a-jar-an`
- `Indonesia` → `In-do-ne-si-a`

---

## 🎯 Fitur Aplikasi

### 1. Dua Cara Pemisahan
- **PUEBI** - Cara resmi dari pemerintah
- **KBBI** - Cara yang lebih detail (memisahkan imbuhan)

### 2. Cek Ejaan
- Bisa deteksi kalau ada typo (salah ketik)
- Kasih saran perbaikan

### 3. Analisis Kata
- Bisa tahu mana awalan (prefix)
- Bisa tahu mana kata dasar (root)
- Bisa tahu mana akhiran (suffix)

---

## 🏗️ Struktur Aplikasi

### File-file Penting

```
📁 Syllable Splitter/
├── 🐍 app.py                          # Program utama (Flask)
├── 📄 requirements.txt                # Daftar library yang dibutuhkan
│
├── 📁 Core Modules/                   # Folder program inti
│   ├── PUEBIOfficialSplitter.py      # Cara PUEBI
│   ├── HybridSyllableSplitter.py     # Cara KBBI
│   ├── KBBISyllableSplitter.py       # Aturan suku kata KBBI
│   ├── MorphologicalAnalyzer.py      # Analisis imbuhan
│   ├── SpellChecker.py               # Cek ejaan
│   └── exceptions.json               # Daftar kata-kata khusus
│
├── 📁 templates/
│   └── index.html                    # Halaman website
│
└── 📁 static/
    └── style.css                     # Tampilan website
```

### Alur Kerja

```
User ketik kata → Cek ejaan (opsional) → Pilih metode → Proses → Hasil
                                              ↓
                                        PUEBI / KBBI
                                              ↓
                                      Pisahkan suku kata
                                              ↓
                                        Tampilkan hasil
```

---

## 📏 Aturan Pemisahan Suku Kata

### Metode PUEBI (Cara Resmi)

#### Aturan 1: Dua Vokal Berurutan
- **Vokal**: a, e, i, o, u
- **Aturan**: Kalau ada 2 vokal berurutan, pisahkan!
- **Contoh**: 
  - `buah` → `bu-ah`
  - `main` → `ma-in`

#### Aturan 2: Diftong (Vokal Kembar)
- **Diftong**: ai, au, ei, oi
- **Aturan**: JANGAN dipisahkan!
- **Contoh**:
  - `pandai` → `pan-dai` ✅ (bukan `pan-da-i` ❌)
  - `saudara` → `sau-da-ra` ✅

#### Aturan 3: Vokal-Konsonan-Vokal (VKV)
- **Aturan**: Pisahkan sebelum konsonan
- **Contoh**:
  - `bapak` → `ba-pak`
  - `lawan` → `la-wan`

#### Aturan 4: Vokal-Konsonan-Konsonan-Vokal (VKKV)
- **Aturan**: Pisahkan di tengah-tengah 2 konsonan
- **Contoh**:
  - `mandi` → `man-di`
  - `sombong` → `som-bong`

#### Aturan 5: Gabungan Konsonan Khusus
- **Konsonan khusus**: ng, ny, sy, kh, ch
- **Aturan**: JANGAN dipisahkan!
- **Contoh**:
  - `banyak` → `ba-nyak` ✅ (bukan `ban-yak` ❌)
  - `syarat` → `sya-rat` ✅

---

### Metode KBBI (Cara Detail)

Metode ini lebih pintar karena bisa memisahkan **imbuhan** (awalan dan akhiran).

#### Langkah 1: Cek Kata Khusus
- Cek apakah kata ada di daftar khusus (`exceptions.json`)
- Kalau ada, pakai yang sudah ditentukan

#### Langkah 2: Cari Imbuhan
- Cari **awalan** (me-, ber-, pe-, dll)
- Cari **kata dasar**
- Cari **akhiran** (-an, -kan, -i, dll)

#### Langkah 3: Pisahkan Setiap Bagian
- Pisahkan awalan jadi suku kata
- Pisahkan kata dasar jadi suku kata
- Tambahkan akhiran

#### Contoh Perbedaan:

**Kata: "pembelajaran"**

| Metode | Hasil | Penjelasan |
|--------|-------|------------|
| PUEBI  | `pem-be-la-ja-ran` | Pisah suku kata biasa |
| KBBI   | `pe-m-be-l-a-jar-an` | `pe` (awalan 1) + `m` (sisipan 1) + `be` (awalan 2) + `l` (sisipan 2) + `a-jar` (kata dasar) + `an` (akhiran) |

---

## 🔍 Analisis Imbuhan

### Jenis-jenis Imbuhan

#### 1. Awalan (Prefix)
Contoh: me-, ber-, pe-, ter-, di-, ke-, se-

**Contoh:**
- `membaca` → awalan: `me`, kata dasar: `baca`
- `berjalan` → awalan: `ber`, kata dasar: `jalan`

#### 2. Akhiran (Suffix)
Contoh: -kan, -an, -i, -nya, -ku, -mu

**Contoh:**
- `bacakan` → kata dasar: `baca`, akhiran: `kan`
- `rumahnya` → kata dasar: `rumah`, akhiran: `nya`

#### 3. Sisipan (Infix)
Huruf yang "nyempil" di tengah awalan.

**Contoh:**
- `pem` → `pe` + `m` (sisipan)
- `pel` → `pe` + `l` (sisipan)
- `bel` → `be` + `l` (sisipan)

#### 4. Awalan Bertingkat (Nested Prefix)
Kata bisa punya lebih dari satu awalan dengan sisipan masing-masing.

**Contoh:**
- `pembelajaran` → `pe` + `m` + `be` + `l` + `ajar` + `an`
  - Awalan pertama: `pe` dengan sisipan `m`
  - Awalan kedua: `be` dengan sisipan `l`
  - Kata dasar: `ajar`
  - Akhiran: `an`

#### 5. Peluluhan (Nasal Assimilation)
Ketika awalan nasal (`me-`, `pe-`, dll) bertemu dengan kata dasar yang dimulai dengan konsonan tertentu, konsonan tersebut **hilang** (luluh) dan digantikan oleh sisipan nasal.

**Aturan Peluluhan:**

| Sisipan | Konsonan Asli | Contoh |
|---------|---------------|--------|
| `m` | `p` | `memisah` = `me` + `m` + **p**isah → `me-m-pi-sah` |
| `n` | `t` | `menari` = `me` + `n` + **t**ari → `me-n-ta-ri` |
| `ng` | `k` | `mengetik` = `me` + `ng` + **k**etik → `me-ng-ke-tik` |
| `ny` | `s` | `menyapu` = `me` + `ny` + **s**apu → `me-ny-sa-pu` |

**Cara Kerja:**
1. Aplikasi menggunakan **lemmatizer** dari `nlp-id` untuk mendeteksi kata dasar
2. Jika kata dasar dimulai dengan konsonan yang luluh (p, t, k, s), konsonan tersebut **dikembalikan**
3. Hasil: awalan + sisipan + **konsonan asli** + sisa kata dasar

**Contoh Detail:**

**memisah** (kata dasar: **pisah**):
- Awalan: `me`
- Sisipan: `m`
- Kata dasar: `pisah` (huruf `p` dikembalikan)
- Hasil: `me-m-pi-sah` ✅

**memakai** (kata dasar: **pakai**):
- Awalan: `me`
- Sisipan: `m` (diambil dari awal detected root)
- Kata dasar: `pakai` (huruf `p` dikembalikan)
- Hasil: `me-m-pa-kai-i` ✅

**mengetik** (kata dasar: **ketik**):
- Awalan: `me`
- Sisipan: `ng`
- Kata dasar: `ketik` (huruf `k` dikembalikan)
- Hasil: `me-ng-ke-tik` ✅

---

## ✅ Cek Ejaan (Spell Checker)

### Cara Deteksi Typo

#### 1. Terlalu Banyak Konsonan
- Kalau ada 5+ konsonan berurutan → **TYPO!**
- Contoh: `pmbljrn` ❌ (7 konsonan berurutan)

#### 2. Huruf Berulang
- Kalau ada huruf sama 3+ kali berurutan → **TYPO!**
- Contoh: `mmmembaca` ❌ (m berulang 3x)

#### 3. Tidak Ada Vokal
- Kalau kata panjang tapi tidak ada vokal → **TYPO!**
- Contoh: `bljr` ❌ (tidak ada vokal)

### Saran Perbaikan
Aplikasi akan kasih saran kata yang mungkin benar:
- `bljr` → saran: `belajar`, `bejar`

---

## 🔌 API (Cara Pakai dari Program Lain)

### 1. Pisahkan Suku Kata

**Kirim ke:** `POST /split`

**Data yang dikirim:**
```json
{
  "text": "pembelajaran Indonesia",
  "method": "kbbi"
}
```

**Hasil yang didapat:**
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
  "method": "kbbi"
}
```

### 2. Cek Ejaan

**Kirim ke:** `POST /check_spelling`

**Data yang dikirim:**
```json
{
  "text": "pmbljrn"
}
```

**Hasil yang didapat:**
```json
{
  "has_typos": true,
  "typos": [
    {
      "word": "pmbljrn",
      "is_correct": false,
      "reason": "Terlalu banyak konsonan berurutan",
      "suggestions": []
    }
  ]
}
```

---

## 🛠️ Teknologi yang Dipakai

### Backend (Program di Server)
- **Python 3.12** - Bahasa pemrograman
- **Flask 3.0.0** - Framework web
- **nlp-id** - Library untuk analisis bahasa Indonesia
- **pyspellchecker** - Library untuk cek ejaan

### Frontend (Tampilan Website)
- **HTML5** - Struktur halaman
- **CSS3** - Desain dan warna
- **JavaScript** - Interaksi dinamis
- **Google Fonts (Inter)** - Font keren

---

## 🚀 Cara Menjalankan Aplikasi

### 1. Install Library
```bash
# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate  # Mac/Linux
# atau
venv\Scripts\activate  # Windows

# Install semua library
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi
```bash
python app.py
```

### 3. Buka di Browser
Buka browser, ketik: `http://127.0.0.1:5000`

---

## 📝 Daftar Kata Khusus (Exception Dictionary)

File: `exceptions.json`

Berisi kata-kata yang punya aturan pemisahan khusus:

```json
{
  "belajar": ["bel", "a", "jar"],
  "pelajar": ["pel", "a", "jar"],
  "ajar": ["a", "jar"],
  "bangun": ["ba", "ngun"],
  "tangan": ["ta", "ngan"]
}
```

**Kenapa perlu?**
- Ada kata yang tidak mengikuti aturan umum
- Agar hasil lebih akurat sesuai KBBI

---

## 🧪 Contoh Testing

### Test PUEBI
```
pembelajaran   → pem-be-la-ja-ran
Indonesia      → In-do-ne-si-a
komputer       → kom-pu-ter
membaca        → mem-ba-ca
banyak         → ba-nyak
```

### Test KBBI
```
pembelajaran   → pe-m-be-l-a-jar-an
Indonesia      → In-do-ne-si-a
komputer       → kom-pu-ter
membaca        → me-m-ba-ca
banyak         → ba-nyak

# Test Peluluhan (Nasal Assimilation)
memisah        → me-m-pi-sah
memakai        → me-m-pa-kai-i
mengetik       → me-ng-ke-tik
menyapu        → me-ny-sa-pu
memasak        → me-m-pa-sak
```

---

## 📚 Referensi

### Dokumen Resmi
1. **PUEBI** - Pedoman Umum Ejaan Bahasa Indonesia
   - Dari: Kementerian Pendidikan dan Kebudayaan
   - Link: https://repositori.kemendikdasmen.go.id/270/1/PUEBI.pdf

2. **KBBI Online**
   - Dari: Badan Pengembangan dan Pembinaan Bahasa
   - Link: https://kbbi.kemdikbud.go.id/

### Library yang Dipakai
1. **syllable_splitter** - Library dasar pemisah suku kata
2. **nlp-id** - Tools NLP bahasa Indonesia
3. **pyspellchecker** - Library cek ejaan

---

## 💡 Kesimpulan

### Perbedaan PUEBI vs KBBI

| Aspek | PUEBI | KBBI |
|-------|-------|------|
| **Fokus** | Pemisahan suku kata murni | Pemisahan + analisis imbuhan |
| **Hasil** | Suku kata saja | Awalan + sisipan + kata dasar + akhiran |
| **Contoh** | `pem-be-la-ja-ran` | `pe-m-be-l-a-jar-an` |
| **Kegunaan** | Untuk ejaan umum | Untuk analisis linguistik |

### Kapan Pakai Yang Mana?

- **Pakai PUEBI** kalau:
  - Cuma butuh pisah suku kata biasa
  - Untuk keperluan ejaan
  
- **Pakai KBBI** kalau:
  - Butuh tahu imbuhan
  - Untuk analisis bahasa
  - Untuk riset linguistik

---

**Selesai! 🎉**

Semoga dokumentasi ini mudah dipahami dan membantu presentasi kamu!
