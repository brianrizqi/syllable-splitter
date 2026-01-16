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

1. **Setup dan Import** - Mengimport modul yang diperlukan
2. **Inisialisasi Splitter** - Membuat instance HybridSyllableSplitter
3. **Contoh Penggunaan Dasar** - Memisahkan kata tunggal
4. **Batch Processing** - Memisahkan banyak kata sekaligus
5. **Analisis Morfologi** - Analisis detail kata kompleks
6. **Perbandingan Metode** - Membandingkan Hybrid, PUEBI, dan KBBI splitter
7. **Uji Kasus Peluluhan** - Testing kasus nasal assimilation
8. **Input Interaktif** - Mencoba kata sendiri
9. **Analisis Batch dari File** - Menggunakan pandas untuk batch processing
10. **Export ke CSV** - Menyimpan hasil ke file CSV

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
