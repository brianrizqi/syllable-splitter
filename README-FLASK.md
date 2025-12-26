# 🐍 Syllable Splitter - Flask Web App (Python Backend)

Aplikasi web untuk memisahkan kata menjadi suku kata dalam bahasa Indonesia menggunakan **Python Flask** sebagai backend.

## 🚀 Cara Menjalankan

### 1. Install Dependencies

Pertama, install Flask terlebih dahulu:

```bash
pip3 install -r requirements.txt
```

atau install langsung:

```bash
pip3 install Flask
```

### 2. Jalankan Server Flask

```bash
python3 app.py
```

Server akan berjalan di: **http://127.0.0.1:5000**

### 3. Buka di Browser

Buka browser dan akses:
```
http://127.0.0.1:5000
```

## ✨ Fitur

- ✅ **Backend Python** - Menggunakan Flask untuk processing
- ✅ **Algoritma Asli** - Menggunakan `SyllableSplitter.py` yang sudah ada
- ✅ **Desain Modern** - Dark theme dengan animasi smooth
- ✅ **Responsive** - Bisa digunakan di HP, tablet, atau komputer
- ✅ **AJAX Request** - Real-time processing tanpa reload halaman
- ✅ **Loading Indicator** - Spinner saat memproses
- ✅ **Copy Hasil** - Salin hasil dengan satu klik

## 📁 Struktur File

```
Syllable Splitter/
├── app.py                    # Flask application
├── SyllableSplitter.py       # Core algorithm (Python class)
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # HTML template
└── static/
    └── style.css            # CSS styling
```

## 🔧 Teknologi

- **Backend**: Python 3.12+ dengan Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Algorithm**: SyllableSplitter (Python)
- **Fonts**: Google Fonts (Inter)

## 📝 API Endpoint

### POST `/split`

Request:
```json
{
  "text": "pembelajaran Indonesia"
}
```

Response:
```json
{
  "results": [
    {
      "word": "pembelajaran",
      "syllables": ["pem", "be", "la", "ja", "ran"]
    },
    {
      "word": "Indonesia",
      "syllables": ["In", "do", "ne", "si", "a"]
    }
  ]
}
```

## 🎯 Cara Menggunakan

1. Ketik kata atau kalimat di kotak input
2. Klik tombol "Pisahkan Suku Kata" atau tekan Enter
3. Tunggu sebentar (akan muncul loading spinner)
4. Lihat hasil pemisahan suku kata
5. Klik "Salin" untuk copy hasil

## 🛠️ Development Mode

Server Flask berjalan dalam debug mode secara default. Untuk production, ubah di `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

## 🙏 Credit

Based on [syllable_splitter](https://github.com/fahadh4ilyas/syllable_splitter) by fahadh4ilyas

---

**Selamat mencoba! 🎉**
