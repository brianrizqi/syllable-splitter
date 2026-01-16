# Jupyter Notebooks untuk Syllable Splitter

Folder ini berisi Jupyter Notebooks untuk menjalankan dan menguji Indonesian Syllable Splitter.

## Cara Menggunakan

### 1. Install Jupyter Notebook

Jika belum terinstall, install Jupyter dengan pip:

```bash
pip install jupyter notebook
```

Atau jika menggunakan virtual environment:

```bash
# Aktifkan virtual environment terlebih dahulu
source ../venv/bin/activate  # untuk Mac/Linux
# atau
..\venv\Scripts\activate  # untuk Windows

# Install Jupyter
pip install jupyter notebook pandas
```

### 2. Jalankan Jupyter Notebook

Dari folder `jupyter_notebooks`, jalankan:

```bash
jupyter notebook
```

Atau dari root folder project:

```bash
cd jupyter_notebooks
jupyter notebook
```

Browser akan otomatis terbuka dengan Jupyter Notebook interface.

### 3. Buka Notebook

Klik pada file `syllable_splitter_demo.ipynb` untuk membuka notebook demo.

## Isi Notebook

Notebook `syllable_splitter_demo.ipynb` mencakup:

### BAGIAN 1: Local Splitter (Offline)
1. **Setup dan Import** - Mengimport semua modul yang diperlukan
2. **Inisialisasi Splitter** - Setup Hybrid, PUEBI Splitter, dan KBBI Scraper
3. **Memisahkan Kata Tunggal** - Contoh dasar
4. **Batch Processing** - Memisahkan banyak kata sekaligus
5. **Analisis Morfologi** - Analisis detail kata kompleks
6. **Perbandingan Metode Local** - Membandingkan Hybrid dan PUEBI splitter
7. **Uji Kasus Peluluhan** - Testing kasus nasal assimilation

### BAGIAN 2: KBBI Scraper (Online)
8. **Scraping dari KBBI** - Mengambil data langsung dari website KBBI
9. **Batch Processing KBBI** - Scraping beberapa kata dengan delay
10. **Perbandingan Online vs Offline** - Membandingkan KBBI Scraper vs Hybrid Splitter

### BAGIAN 3: Analisis dan Export
11. **Input Interaktif** - Mencoba kata sendiri (offline + online)
12. **Analisis Batch dengan Pandas** - Batch processing dengan dataframe
13. **Export ke CSV** - Menyimpan hasil ke file CSV
14. **Kesimpulan** - Perbandingan metode dan rekomendasi penggunaan

**Catatan Penting:**
- Method yang benar adalah `split_syllables()` bukan `split()`
- KBBI Scraper membutuhkan koneksi internet
- Gunakan delay saat scraping untuk tidak membebani server KBBI

## Tips

- Jalankan cell secara berurutan dengan menekan `Shift + Enter`
- Gunakan `Ctrl + Enter` untuk menjalankan cell tanpa pindah ke cell berikutnya
- Restart kernel jika ada error: Menu → Kernel → Restart

## Troubleshooting

Jika ada error "Module not found":
1. Pastikan Anda menjalankan notebook dari folder `jupyter_notebooks`
2. Pastikan semua dependencies sudah terinstall (lihat `requirements.txt` di root folder)
3. Pastikan path ke parent directory sudah benar di cell pertama

## Requirements

- Python 3.6+
- Jupyter Notebook
- pandas (untuk analisis batch)
- Semua dependencies dari `requirements.txt` di root folder
