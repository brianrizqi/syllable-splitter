# Laporan Implementasi Pemenggalan Suku Kata (SylBI)

Dokumen ini merangkum arsitektur dan aturan pemenggalan yang **benar-benar berlaku pada kode saat ini**. Semua contoh hasil di bawah diambil langsung dari keluaran program (bukan target ideal).

> Terakhir diperbarui: 27 Juli 2026 (mengikuti commit `a97bc8a` di `main`).

---

## 1. Arsitektur: Tiga Lapis + Kamus

Untuk metode **SylBI**, sebuah kata diproses dengan urutan prioritas:

1. **KBBI daring (prioritas utama)** — `KBBIScraper` mengambil data langsung dari situs KBBI. Bila kata ditemukan, pemenggalan dan *root hint* diambil dari sana. Ini memastikan **kata baru tetap terlayani** tanpa menunggu pembaruan kamus lokal.
2. **Basis data validasi** — hasil koreksi manual yang tersimpan (`SyllableValidationDB`) dipakai sebagai cadangan.
3. **Algoritma SylBI luring (fallback)** — `HybridSyllableSplitter` + `MorphologicalAnalyzer` memenggal secara morfemis-fonetis. Dipakai untuk pemrosesan massal (CSV), saat KBBI daring lambat/mati, dan saat luring.

### Kamus disambiguasi (`kbbi_words.txt`)
Algoritma luring memakai daftar ±71.000 kata dasar KBBI untuk **memutuskan apakah sebuah kata benar-benar berimbuhan**. Tanpa kamus ini, penganalisis akan memenggal kata dasar yang hanya *tampak* berimbuhan (mis. `pencet` → `peng-cet`). Kamus:
- Dimuat oleh `MorphologicalAnalyzer` dan `SpellChecker`.
- **Diperkaya otomatis (self-learning)**: setiap kata yang berhasil diambil dari KBBI daring ditambahkan ke kamus di memori.
- Dapat diregenerasi berkala via `scripts/refresh_kbbi_words.py`.

Endpoint `GET /health` menampilkan `kbbi_dict_size` untuk memastikan kamus termuat di lingkungan produksi.

---

## 2. Konvensi Pemenggalan yang Berlaku

- **Awalan nasal verba** (`me-`, `mem-`, `men-`, `meng-`, `meny-`) ditampilkan dalam **bentuk baku `meng-`**, dan **akar kata dipulihkan** bila mengalami peluluhan (k/p/t/s). Contoh: `menulis` → `meng-tu-lis` (akar *tulis*), `memukul` → `meng-pu-kul` (akar *pukul*).
- **Awalan nominalisasi** (`pe-`, `pem-`, `pen-`, `peng-`, `peny-`) ditampilkan baku **`peng-`**.
- **Awalan lain** (`ber-`, `ter-`, `per-`, `di-`, `ke-`, `se-`) ditampilkan apa adanya.
- **Kata dasar dipenggal secara fonetis**; kata dasar yang utuh dilindungi kamus agar tidak salah pecah.

---

## 3. Aturan per Kategori (hasil aktual)

### a. Kata dasar (tanpa imbuhan)
| Kata | Hasil |
| :-- | :-- |
| komputer | `kom-pu-ter` |
| modifikasi | `mo-di-fi-ka-si` |
| arteri | `ar-te-ri` |
| pencet | `pen-cet` |
| penyu | `pe-nyu` |

### b. Awalan `me-`/`peN-` + peluluhan (baku `meng-`/`peng-`)
| Kata | Hasil |
| :-- | :-- |
| menulis | `meng-tu-lis` |
| memukul | `meng-pu-kul` |
| menyapu | `meng-sa-pu` |
| mengambil | `meng-am-bil` |
| pembeli | `peng-be-li` |
| pengambil | `peng-am-bil` |

### c. `di-` / `ter-` / `ber-` / `per-` / `ke-` / `se-`
| Kata | Hasil |
| :-- | :-- |
| dibelikan | `di-be-li-kan` |
| terbawa | `ter-ba-wa` |
| berjalan | `ber-ja-lan` |
| kebersihan | `ke-ber-sih-an` |
| setahuku | `se-ta-hu-ku` |

### d. Sufiks & Konfiks
| Kata | Hasil |
| :-- | :-- |
| masukkan | `ma-suk-kan` |
| makanan | `ma-kan-an` |
| kecurian | `ke-cu-ri-an` |
| kekuatan | `ke-ku-at-an` |
| perbuatan | `per-bu-at-an` |

---

## 4. Perbaikan Penting

### A. Root-Preserving via Kamus
Kata dasar yang hanya *tampak* berimbuhan tidak lagi dipenggal salah: `pencet` → `pen-cet` (bukan `peng-cet`), `modifikasi` → `mo-di-fi-ka-si` (bukan `mo-di-fi-kas-i`), `perang` → `pe-rang`, `meja` → `me-ja`.

### B. Prefiks Ganda (base tetap utuh)
Kata dasar yang kebetulan diawali huruf awalannya sendiri kini tidak kehilangan suku kata:
| Kata | Hasil |
| :-- | :-- |
| terteror | `ter-te-ror` |
| terteruskan | `ter-te-rus-kan` |
| berberes | `ber-be-res` |
| berberita | `ber-be-ri-ta` |

### C. Imbuhan Bertumpuk
Batas morfem dalam kata berimbuhan ganda dipertahankan (diurai satu tingkat lagi, hanya bila akar dalamnya kata KBBI sah):
| Kata | Hasil |
| :-- | :-- |
| berkehidupan | `ber-ke-hi-dup-an` |
| berkeharusan | `ber-ke-ha-rus-an` |
| berpenghasilan | `ber-peng-ha-sil-an` |
| berkepentingan | `ber-ke-pen-ting-an` |

### D. Reduplikasi Berimbuhan
Kata ulang berimbuhan disusun ulang sebagai `awalan + basis-reduplikasi + akhiran` memakai *root hint* dari KBBI (basis yang ber-tanda hubung):
| Kata (root hint) | Hasil |
| :-- | :-- |
| memontang-mantingkan (*pontang-panting*) | `meng-pon-tang-pan-ting-kan` |
| memorak-porandakan (*porak-poranda*) | `meng-po-rak-po-ran-da-kan` |

### E. Infiks (`-el-`, `-er-`, `-em-`, `-in-`)
Deteksi infiks kini dijaga kamus agar tidak salah picu pada kata dasar sungguhan (`sebelum` tidak lagi jadi `se-bum-el`). Kata berinfiks yang sah tetap ditangani, mis. `telunjuk` → `tun-el-juk`.

---

## 5. Keterbatasan yang Diketahui (luring)

Semua ini teratasi di produksi lewat jalur **KBBI daring** (prioritas utama); yang tersisa hanya pada algoritma luring:

- **Ambiguitas tak terpecahkan**: akar pendek yang kebetulan kata sah, mis. `memiriskan` → `meng-i-ris-kan` (*miris* vs *iris*).
- **Partikel pada headword**: `apakah` → `a-pa-kah` (partikel `kah` belum dipisah).
- **Sebagian analisis ambigu**: mis. `pemain` → `peng-ma-in`.

---

## 6. Komponen Teknis

- **`HybridSyllableSplitter.py`** — orkestrasi morfemis-fonetis, restorasi peluluhan, reduplikasi, prefiks ganda.
- **`MorphologicalAnalyzer.py`** — dekomposisi awalan/akhiran/konfiks, guard berbasis kamus, dekomposisi imbuhan bertumpuk, deteksi infiks.
- **`KBBIScraper.py`** — pengambilan data KBBI daring (prioritas utama).
- **`SyllableValidationDB.py`** — penyimpanan validasi manual.
- **`kbbi_words.txt`** + **`scripts/refresh_kbbi_words.py`** — kamus disambiguasi + regenerasi.

---

## Catatan Konvensi (perlu keputusan)

Kode saat ini memakai konvensi **"suku kata penuh"** untuk kata turunan (mis. `berjalan` → `ber-ja-lan`, `membaca` → `meng-ba-ca`).

Terdapat arahan alternatif dari Pak Daniel (mengacu PUEBI pemenggalan kata turunan): **bentuk dasar yang tidak berubah dibiarkan utuh** — mis. `berjalan` → `ber-jalan`, `membantu` → `meng-bantu`, `makanan` → `makan-an`; sedangkan bentuk dasar yang berubah (peluluhan) tetap dipenggal — mis. `menguatkan` → `meng-ku-at-kan`. Aturan ini **belum aktif** di kode saat ini (sempat diterapkan lalu di-*rollback*). Bila hendak diaktifkan, laporan ini perlu diperbarui lagi.
