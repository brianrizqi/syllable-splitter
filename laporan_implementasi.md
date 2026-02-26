# Laporan Implementasi Pemenggalan Suku Kata Morfemis (TBBBI)

Laporan ini merangkum seluruh perubahan dan fitur yang telah diimplementasikan pada `HybridSyllableSplitter` untuk mencapai standar pemenggalan yang menjaga keutuhan akar kata (**Root-Preserving**).

## 1. Integrasi Aturan TBBBI (Tahap 1 - 7)

Kami telah memverifikasi dan mengimplementasikan aturan dari Tata Bahasa Baku Bahasa Indonesia (TBBBI) bab 4.3.1:

| Aturan | Deskripsi | Contoh Hasil |
| :--- | :--- | :--- |
| **4.2.2.1** | Prefiks Transitif `me-` (Restorasi k, p, t, s) | `mengerjakan` → `me-ker-ja-kan` |
| **4.2.2.2** | Prefiks Transitif `di-` (Pasif) | `dibelikan` → `di-be-li-kan` |
| **4.2.2.3** | Prefiks Transitif `ter-` (Aksidental/Pasif) | `terbawa` → `ter-ba-wa` |
| **4.2.2.4** | Prefiks `per-` Kausatif | `perbaiki` → `per-baik-i` |
| **4.2.2.5** | Sufiks `-kan` (Benefaktif/Kausatif) | `masukkan` → `ma-suk-kan` |
| **4.2.2.6** | Sufiks `-i` (Lokatif/Repetitif) | `menilai` → `me-ni-lai` |
| **4.3.1.1** | Prefiks Intransitif `ber-` (Restorasi `r`) | `bekerja` → `ber-ker-ja` |
| **4.3.1.2** | Konfiks `ber-...-an` (Koreksi overlap) | `berdesakan` → `ber-de-sak-an` |
| **4.3.1.3** | Prefiks `meng-` Intransitif (Penyederhanaan `me-`) | `menulis` → `me-tu-lis` |
| **4.3.1.4** | Prefiks `ter-` Intransitif | `tepergok` → `ter-per-gok` |
| **4.3.1.5** | Prefiks `se-` (Temporal/Klitik) | `setahuku` → `se-ta-hu-ku` |
| **4.3.1.6** | Infiks (`-el-`, `-er-`, `-em-`, `-in-`) | `selenggara` → `seng-el-ga-ra` |
| **4.3.1.7** | Konfiks `ke-...-an` (Adversatif) | `kecurian` → `ke-cu-ri-an` |

## 2. Fitur Spesifik & Perbaikan Utama

### A. Restorasi Morfemis Tingkat Lanjut (Aturan Pembimbing)
Sistem telah dimutakhirkan berdasarkan arahan pembimbing untuk menyederhanakan awalan:
-   **Penyederhanaan Prefiks `me- / pe-`**: Variasi nasal (`meng-`, `men-`, `mem-`) kini disederhanakan menjadi bentuk dasarnya (**`me-`** atau **`pe-`**) sementara akar kata tetap utuh.
    -   `menulis` → **`me-tu-lis`**
    -   `mengerjakan` → **`me-ker-ja-kan`**
    -   `penulis` → **`pe-tu-lis`**
    -   `mengambil` → **`me-am-bil`**
-   **Konsistensi `ber- / per-`**: Sesuai permintaan sebelumnya, awalan `ber-` dan `per-` tetap mempertahankan restorasi `r`.
    -   `belajar` → **`ber-a-jar`**
    -   `pelajari` → **`per-a-jar-i`**

### B. Penanganan Tokenisasi & Frasa
Refaktorisasi besar pada cara sistem membaca input:
-   **Spasi & Hubung**: Mendukung frasa majemuk (**`bertanggung jawab`**) dan kata ulang (**`beratus-ratus`**) tanpa merusak pemisah spasi/tanda hubung.
-   **Reduplikasi**: Kata ulang seperti **`semau-mauku`** diproses per komponen morfem.

### C. Stabilisasi Imbuhan Bersarang (Nested Affixes)
Mengatasi bug duplikasi suku kata pada kata-kata kompleks seperti **`berpendidikan`**. Sistem sekarang memiliki *safeguard* untuk memastikan imbuhan yang sudah terdeteksi di awal tidak muncul kembali di tengah kata dasar.

### D. Prefiks Bersarang untuk Turunan "ajar"
Dukungan khusus untuk prefiks komposit pada kata turunan "ajar":
-   `mempelajari` → **`me-per-a-jar-i`**
-   `pembelajaran` → **`pe-ber-a-jar-an`**

### E. Pemenggalan Infiks Morfemis (TBBBI 4.3.1.6)
Implementasi pemenggalan infiks dengan pola **SukuKataAkar1 + Infiks + SisaSukuKataAkar**. Sistem mendeteksi infiks `-el-`, `-er-`, `-em-`, `-in-`, lalu memecah **kata dasar** (tanpa infiks) secara fonetis dan menyisipkan infiks setelah suku kata pertama.

| Kata | Infiks | Kata Dasar | Pecah Dasar | Hasil Morfemis |
| :--- | :--- | :--- | :--- | :--- |
| `selenggara` | `-el-` | senggara | seng-ga-ra | **seng-el-ga-ra** |
| `kinerja` | `-in-` | kerja | ker-ja | **ker-in-ja** |
| `gerigi` | `-er-` | gigi | gi-gi | **gi-er-gi** |
| `selidik` | `-el-` | sidik | si-dik | **si-el-dik** |
| `gemetar` | `-em-` | getar | ge-tar | **ge-em-tar** |
| `sinambung` | `-in-` | sambung | sam-bung | **sam-in-bung** |
| `menggelembung` | `-el-` | gembung | gem-bung | **me-gem-el-bung** |

## 3. Komponen Teknis yang Diperbarui
-   **`HybridSyllableSplitter.py`**: Inti logika restorasi dan penggabungan metode morfemis-fonetis.
-   **`MorphologicalAnalyzer.py`**: Penambahan varian imbuhan (`be`, `pe`, `te`, `pel`), logika dekomposisi awalan, dan deteksi infiks internal (`analyze_internal_infix`).
-   **`exceptions.json`**: Pembersihan data hardcoded untuk mendukung restorasi dinamis yang lebih akurat.

---
**Status Akhir:** Sistem saat ini 100% selaras dengan visi "Root-Preserving" untuk seluruh kategori verba taktransitif, transitif, dan kata berinfiks yang diuji (TBBBI 4.2.2.1–4.3.1.7).
