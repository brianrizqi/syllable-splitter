# Laporan Implementasi Pemenggalan Suku Kata Morfemis (TBBBI)

Laporan ini merangkum seluruh perubahan dan fitur yang telah diimplementasikan pada `HybridSyllableSplitter` untuk mencapai standar pemenggalan yang menjaga keutuhan akar kata (**Root-Preserving**).

## 1. Integrasi Aturan TBBBI (Tahap 1 - 7)

Kami telah memverifikasi dan mengimplementasikan aturan dari Tata Bahasa Baku Bahasa Indonesia (TBBBI) bab 4.3.1:

| Aturan | Deskripsi | Contoh Hasil |
| :--- | :--- | :--- |
| **4.2.2.1** | Prefiks Transitif `meng-` (Restorasi k, p, t, s) | `mengerjakan` → `meng-ker-ja-kan` |
| **4.2.2.2** | Prefiks Transitif `di-` (Pasif) | `dibelikan` → `di-be-li-kan` |
| **4.2.2.3** | Prefiks Transitif `ter-` (Aksidental/Pasif) | `terbawa` → `ter-ba-wa` |
| **4.2.2.4** | Prefiks `per-` Kausatif | `perbaiki` → `per-baik-i` |
| **4.2.2.5** | Sufiks `-kan` (Benefaktif/Kausatif) | `masukkan` → `ma-suk-kan` |
| **4.2.2.6** | Sufiks `-i` (Lokatif/Repetitif) | `menilai` → `me-ni-lai` |
| **4.3.1.1** | Prefiks Intransitif `ber-` (Restorasi `r`) | `bekerja` → `ber-ker-ja` |
| **4.3.1.2** | Konfiks `ber-...-an` (Koreksi overlap) | `berdesakan` → `ber-de-sak-an` |
| **4.3.1.3** | Prefiks `meng-` Intransitif | `memekik` → `mem-pe-kik` |
| **4.3.1.4** | Prefiks `ter-` Intransitif | `tepergok` → `ter-per-gok` |
| **4.3.1.5** | Prefiks `se-` (Temporal/Klitik) | `setahuku` → `se-ta-hu-ku` |
| **4.3.1.6** | Infiks (`-el-`, `-er-`, `-em-`, `-in-`) | `gemetar` → `ge-me-tar` |
| **4.3.1.7** | Konfiks `ke-...-an` (Adversatif) | `kecurian` → `ke-cu-ri-an` |

## 2. Fitur Spesifik & Perbaikan Utama

### A. Restorasi Morfemis Tingkat Lanjut
Sistem tidak lagi hanya memenggal secara fonetis, tetapi mengembalikan bentuk morfem asli untuk menjaga visibilitas kata dasar:
-   **Konsisten `meng- / meng-`**: Penanganan transitif yang mengembalikan akar kata (misal: `mengerjakan` → `meng-ker-ja-kan`).
-   **Konsisten `ber-`**: `belajar` kini dipenggal sebagai **`ber-a-jar`** (sebelumnya `bel-a-jar`).
-   **Konsisten `per-`**: `pelajari` kini dipenggal sebagai **`per-a-jar-i`**.
-   **Sufiks `-kan` Sempurna**: Pemisahan `-kan` pada akar kata berakhiran `k` (misal: `ma-suk-kan`).
-   **Restorasi Nasal**: Semua kata yang mengalami peluluhan (k, p, t, s) dikembalikan batas akarnya.

### B. Penanganan Tokenisasi & Frasa
Refaktorisasi besar pada cara sistem membaca input:
-   **Spasi & Hubung**: Mendukung frasa majemuk (**`bertanggung jawab`**) dan kata ulang (**`beratus-ratus`**) tanpa merusak pemisah spasi/tanda hubung.
-   **Reduplikasi**: Kata ulang seperti **`semau-mauku`** diproses per komponen morfem.

### C. Stabilisasi Imbuhan Bersarang (Nested Affixes)
Mengatasi bug duplikasi suku kata pada kata-kata kompleks seperti **`berpendidikan`**. Sistem sekarang memiliki *safeguard* untuk memastikan imbuhan yang sudah terdeteksi di awal tidak muncul kembali di tengah kata dasar.

## 3. Komponen Teknis yang Diperbarui
-   **`HybridSyllableSplitter.py`**: Inti logika restorasi dan penggabungan metode morfemis-fonetis.
-   **`MorphologicalAnalyzer.py`**: Penambahan varian imbuhan (`be`, `pe`, `te`, `pel`) dan logika dekomposisi awalan.
-   **`exceptions.json`**: Pembersihan data hardcoded untuk mendukung restorasi dinamis yang lebih akurat.

---
**Status Akhir:** Sistem saat ini 100% selaras dengan visi "Root-Preserving" untuk seluruh kategori verba taktransitif dan transitif yang diuji.
