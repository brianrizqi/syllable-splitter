# Laporan Implementasi Pemenggalan Suku Kata (SylBI)

Dokumen ini merangkum arsitektur dan aturan pemenggalan yang **benar-benar berlaku pada kode saat ini**. Semua contoh hasil di bawah diambil langsung dari keluaran program (bukan target ideal).

> Terakhir diperbarui: 19 Oktober 2026.

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

### Peta kata dasar (`kbbi_roots.tsv`)
`kbbi_words.txt` memuat kata dasar **dan** kata turunan, sehingga tidak bisa membedakan keduanya. Untuk itu dipakai peta ±26.700 kata turunan → kata dasar, dibangun dari kolom `kata_dasar` data KBBI (`scripts/build_kbbi_roots.py`). Bila KBBI daring tidak memberi hasil, kata dasar dari peta ini dipakai sebagai *root hint*, sehingga hasil luring sama dengan hasil jalur daring (mis. `menguati` → *kuat* → `meng-ku-at-i`).
- Kata yang di KBBI sekaligus kata dasar dan kata turunan (mis. `mereka` "pronomina" vs *me-* + *reka*) tidak dimasukkan, agar tetap ditangani seperti sebelumnya.
- Bila KBBI mencatat lebih dari satu kata dasar, dipakai yang pertama (sama dengan jalur daring), mis. `mengemaskan` → *emas* → `meng-e-mas-kan`.
- *Golden map* (koreksi manual peneliti) tetap didahulukan di atas peta ini.

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
Deteksi infiks kini dijaga kamus agar tidak salah picu pada kata dasar sungguhan (`sebelum` tidak lagi jadi `se-bum-el`). Kata berinfiks yang sah tetap ditangani, mis. `kelupas` → `ku-el-pas`. Pengecualian: `telunjuk` dipenggal sebagai kata dasar sesuai EYD V (`te-lun-juk`), karena maknanya berbeda dari *tunjuk*.

### F. Kata Turunan saat KBBI Daring Tidak Tersedia
Sebelumnya, kata turunan yang tercantum di `kbbi_words.txt` dianggap kata dasar oleh jalur luring, sehingga awalan tidak dipisah dan konsonan luluh tidak dipulihkan. Dengan peta kata dasar, hasilnya kini mengikuti kata dasar KBBI:
| Kata | Sebelum | Sesudah |
| :-- | :-- | :-- |
| menguati | `me-ngu-a-ti` | `meng-ku-at-i` |
| menyerepi | `me-nye-re-pi` | `meng-se-rep-i` |
| mengamuskan | `me-nga-mus-kan` | `meng-ka-mus-kan` |
| memurukkan | `meng-u-ruk-kan` | `meng-pu-ruk-kan` |
| mengerakali | `me-nge-ra-ka-li` | `meng-ke-ra-kal-i` |

Perbaikan terkait:
- **Imbuhan bertumpuk dengan *root hint***: `memberdayakan` → `meng-ber-da-ya-kan` (sebelumnya `ber` hilang), `memerhatikan` → `meng-per-ha-ti-kan`, `ketidakadilan` → `ke-ti-da-ka-dil-an`.
- **Dwipurwa** tidak lagi dibaca sebagai awalan `ter-`/`ber-`/`peng-`: `tetua` → `te-tu-a`, `beberapa` → `be-be-ra-pa`, `pepatah` → `pe-pa-tah`.

### G. Penyesuaian dengan EYD Edisi V (2022)
Metode yang sebelumnya bernama **PUEBI** kini bernama **EYD** (arahan Pak Daniel), di aplikasi maupun di kode (`EYDSplitter`). Nilai `method` di API adalah `eyd`; nilai lama `puebi` tetap diterima, dan data validasi lama tetap tersimpan dengan kunci `puebi`.

Rujukan ejaan kini **EYD Edisi V** (Keputusan Kepala Badan Bahasa No. 0424/I/BS.00.01/2022), yang menggantikan PUEBI. Aturan pemenggalan kata dasarnya sama dengan PUEBI 2016, kecuali dua hal yang kini ditangani:
- **Monoftong *eu* tidak dipenggal**: `seudati` → `seu-da-ti`, `cileuncang` → `ci-leun-cang`, `geulis` → `geu-lis`. Karena *eu* hanya monoftong bila dilafalkan [ə], aturan mengikuti pemenggalan KBBI untuk 34 kata yang bersangkutan (`eu_monophthong.json`, dibangun oleh `scripts/build_eu_monophthong.py`); kata lain tetap dipenggal `e-u` (`e-u-fe-mis-me`, `ke-u-ang-an`).
- **Diftong di tengah kata** sebelum satu konsonan + vokal tidak lagi dipenggal pada splitter gaya KBBI (dipakai SylBI): `saudara` → `sau-da-ra`, `kaidah` → `kai-dah`, `audit` → `au-dit`. Kesesuaian dengan pemenggalan KBBI untuk kata dasar naik dari 92,42% menjadi 92,74%.

Perbaikan terkait: awalan *me-* tanpa nasal tidak lagi dikenali di depan kata dasar berawal vokal (`meurah` → `meu-rah`, `meander` → `me-an-der`), karena *meN-* di depan vokal selalu menjadi *meng-*.

---

## 5. Keterbatasan yang Diketahui (luring)

Semua ini teratasi di produksi lewat jalur **KBBI daring** (prioritas utama); yang tersisa hanya pada algoritma luring:

- **Ambiguitas tak terpecahkan**: akar pendek yang kebetulan kata sah, mis. `memiriskan` → `meng-i-ris-kan` (*miris* vs *iris*).
- **Partikel pada headword**: `apakah` → `a-pa-kah` (partikel `kah` belum dipisah).
- **Sebagian analisis ambigu**: mis. `pemain` → `peng-ma-in`.
- **Diftong pada batas gabungan kata**: `pendayaupayaan` (*daya* + *upaya*) → `peng-da-yau-pa-ya-an`, `autoimun` → `au-toi-mun`.
- **Kata yang di KBBI tidak punya kata dasar**: mis. `mengerawan` tercatat sebagai nomina dasar (nama pohon, varian *merawan*), sehingga tetap `me-nge-ra-wan`.

---

## 6. Komponen Teknis

- **`HybridSyllableSplitter.py`** — orkestrasi morfemis-fonetis, restorasi peluluhan, reduplikasi, prefiks ganda.
- **`MorphologicalAnalyzer.py`** — dekomposisi awalan/akhiran/konfiks, guard berbasis kamus, dekomposisi imbuhan bertumpuk, deteksi infiks.
- **`KBBIScraper.py`** — pengambilan data KBBI daring (prioritas utama).
- **`SyllableValidationDB.py`** — penyimpanan validasi manual.
- **`kbbi_words.txt`** + **`scripts/refresh_kbbi_words.py`** — kamus disambiguasi + regenerasi.
- **`kbbi_roots.tsv`** + **`scripts/build_kbbi_roots.py`** — peta kata turunan → kata dasar untuk jalur luring.
- **`eu_monophthong.json`** + **`EuMonophthong.py`** + **`scripts/build_eu_monophthong.py`** — aturan monoftong *eu* (EYD V).

---

## Catatan Konvensi

Konvensi yang **aktif** untuk kata turunan adalah **"suku kata penuh"**: bentuk dasar tetap dipenggal menjadi suku kata, mis. `berjalan` → `ber-ja-lan`, `membaca` → `meng-ba-ca`, `makanan` → `ma-kan-an`.

Sebagai catatan riwayat: pernah dicoba aturan alternatif (PUEBI pemenggalan kata turunan — bentuk dasar yang tidak berubah dibiarkan utuh, mis. `ber-jalan`, `makan-an`), namun kemudian di-*rollback* sehingga **tidak dipakai**. Laporan ini konsisten dengan kode yang berjalan sekarang.
