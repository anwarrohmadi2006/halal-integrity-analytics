# Navigasi Integritas Halal — Pemetaan Komposisi Pangan Riil Menggunakan Multiple Correspondence Analysis (MCA) dan Sparse RBF Spectral Clustering

**Tugas Proyek Akhir Kelompok — Mata Kuliah: Python untuk Sains Data (Sains Data)**
*Repositori resmi untuk analisis matematika multivariat, visualisasi spasial, dan data storytelling ekosistem pangan komersial di Indonesia ($N = 15.739$ produk).*

---

## 👥 Identitas Anggota Kelompok
| No | Nama | NIM | Peran Utama |
|---|---|---|---|
| 1 | **Anwar Rohmadi** | 247411027 | Ketua / Data Wrangling, Parser, & Automasi Dokumen |
| 2 | **Muhammad Fathir Raihan Al Farici** | 247411007 | Pemodelan Matematika & MCA |
| 3 | **Muhammad Thoriq Yusron Muttaqiin** | 247411016 | Spectral Clustering & Evaluasi Spektral |
| 4 | **Muhammad Rasyid Arrafi** | 247411019 | Proyeksi Spasial UMAP & Visualisasi Kolokasi |
| 5 | **Naufal Ajwa Nurfarros** | 247411024 | Narasi Storytelling & Penyusunan Laporan Akademik |
| 6 | **Ravelino Bagas Pratama** | 247411025 | Validasi Syariah, Presentasi & Pengujian Metrik |

---

## 📌 Ringkasan Proyek
Proyek ini mengusulkan sebuah pendekatan statistika multivariat tingkat lanjut untuk memetakan sebaran produk pangan komersial berdasarkan komposisi biner bahan penyusunnya (*ingredients*). Kami menggabungkan metode reduksi dimensi non-linier **Multiple Correspondence Analysis (MCA)** berbasis kriteria Greenacre dengan metode klasterisasi berbasis graf **Spectral Clustering** menggunakan **Sparse RBF Similarity Matrix**.

Hasil pemodelan dibandingkan secara komparatif dengan algoritma baseline **K-Means Clustering** untuk menguji ketahanan model dalam memetakan struktur data kontinu (*manifold*). Studi ini juga mengintegrasikan visualisasi **Data Storytelling** interaktif untuk membumikan konsep matematis bagi para regulator jaminan produk halal (seperti BPJPH dan LPPOM-MUI) serta masyarakat umum.

---

## 🔬 Metrik Evaluasi Komparatif (K-Means vs. Spectral Clustering)
Pengujian empiris membuktikan keunggulan Spectral Clustering dalam mengurai keterkaitan bahan pangan yang non-konveks dibanding pemotongan linier paksa (*spherical cuts*) K-Means:

| Kategori Pengujian | Nama Metrik | K-Means ($K=8$) | Spectral Clustering ($K=8$) | Interpretasi & Arah Kualitas |
| :--- | :--- | :---: | :---: | :--- |
| **I. Kualitas Manifold** | **10-NN Connectivity Score** | `0.9554` | **`0.9539`** | **Tinggi lebih baik.** Persentase tetangga terdekat di ruang MCA yang berlabel sama (K-Means bias naik akibat klaster C2 raksasa). |
| | **Average Graph Conductance** | `0.1246` | **`0.0936`** | **Rendah lebih baik.** Tingkat kebocoran tepi graf ke luar klaster. **Spectral jauh lebih bersih dan terisolasi.** |
| **II. Asosiasi Kehalalan** | **Cramer's V (Korelasi Halal)** | `0.3853` | **`0.5098`** | **Tinggi lebih baik.** Kekuatan asosiasi klaster terhadap status kehalalan lapangan (Syariah). **Spectral unggul signifikan.** |
| | **Adjusted Mutual Info (AMI)** | `0.1298` | **`0.1450`** | **Tinggi lebih baik.** Informasi timbal-balik klaster-kehalalan. |
| | **Normalized Mutual Info (NMI)** | `0.1302` | **`0.1454`** | **Tinggi lebih baik.** Normalisasi kesamaan informasi timbal-balik. |
| **III. Struktur Geometris** | **Silhouette Score (Euclidean)** | **`0.4136`** | `-0.0807` | **Tinggi lebih baik.** K-Means unggul semu karena Silhouette mengasumsikan bentuk klaster konveks/bola. |
| | **Davies-Bouldin Index (DBI)** | **`1.0663`** | `1.6538` | **Rendah lebih baik.** Mengukur rasio jarak dalam klaster vs. antarklaster secara linier. |
| | **Calinski-Harabasz Index (CHI)** | **`676.1`** | `283.1` | **Tinggi lebih baik.** Rasio dispersi Euclidean antarklaster terhadap dalam klaster. |

---

## 🎨 Galeri Visual & Narasi Data Storytelling (Section 4.6)
Visualisasi utama yang dihasilkan secara otomatis dan disimpan dalam direktori `output_halal/` meliputi:

1. **Grafik 1: Dashboard Overview Ekosistem Pangan (`fig1_dashboard_overview.png`)**
   * *Insight*: Menyajikan statistik makro ekosistem pangan komersial di Indonesia. Menunjukkan *blind spot* besar di mana **73,53%** produk bersertifikat administratif menyembunyikan resep komposisinya, dan 99,8% data gizi bernilai kosong (*sparsity* tinggi).
2. **Grafik 2: Analisis Bahan Bermasalah (`fig2_bahan_bermasalah.png`)**
   * *Insight*: Menyoroti bahan *mushbooh* (syubhat) paling kritis. Gelatin mendominasi dengan kemunculan sebanyak **620 kali**, diiringi visualisasi perbandingan spasial kegagalan pembagian K-Means vs. sensitivitas topologi Spectral.
3. **Grafik 3: Heatmap Ko-kemunculan Bahan (`fig3_cooccurrence_heatmap.png`)**
   * *Insight*: Mengungkap pola formulasi produsen. Menunjukkan fenomena *Hidden in Plain Sight* di mana bahan kritis (seperti flavoring) terikat erat secara spasial dengan bahan universal pendukung seperti daging sapi (*beef*) dan gula dekstrosa (*dextrose*).
4. **Grafik 4: Karakteristik 8 Klaster Produk (`fig4_cluster.png`)**
   * *Insight*: Membuktikan secara empiris teori **Akumulasi Risiko Spasial**—semakin kompleks bahan aditif pada resep produk (seperti Klaster 8 Confectionery dengan rata-rata 11,3 aditif), tingkat kehalalan objektifnya anjlok hingga **82,6%**.
5. **Grafik 5: Infografis Ringkasan Temuan (`fig5_insight_summary.png`)**
   * *Insight*: Rangkuman 6 kartu temuan utama visual untuk konsumsi publik.
6. **Grafik 6: Purwarupa Web Dashboard Interaktif (`fig6_web_dashboard.png`)**
   * *Insight*: Antarmuka visual interaktif berbasis web yang memuat peta spasial proyeksi UMAP 2D serta simulasi Live Recipe Scanner untuk mendeteksi risiko CCP kehalalan komposisi secara otomatis.

---

## 📂 Struktur Repositori
Repositori ini disusun secara modular agar mandiri, bersih, dan mudah digunakan kembali:

```text
tugas_akhir_data_storytelling/
├── data/
│   └── processed/                  # File CSV olahan hasil wrangling & pemodelan
│       ├── halal_products_tabular.csv   # Data tabular hasil parsing RDF Turtle
│       ├── ingredients_halal_status.csv  # Kamus status kehalalan bahan MUI/JAKIM
│       ├── product_spectral_clusters.csv # Koordinat MCA, UMAP, & Label Klaster
│       └── spectral_k_range_results.csv  # Hasil evaluasi rentang K klaster
│   └── products_data.json          # Database produk format JSON untuk Web Dashboard
├── src/                            # Modul utama (Source Code Core)
│   ├── parser.py                   # Parser ekspresi reguler (Turtle to Tabular)
│   ├── classifier.py               # Logika risk propagation status halal
│   ├── modeling.py                 # Pipa MCA & Spectral Clustering (LOBPCG solver)
│   ├── evaluation.py               # Komputasi metrik spasial (Conductance, NMI)
│   └── visualization.py            # Modul penggambaran visualisasi matplotlib/seaborn
├── scripts/                        # Skrip CLI untuk eksekusi alur
│   ├── extract_data.py             # Menjalankan ETL data RDF Turtle
│   ├── run_modeling.py             # Menjalankan pemodelan spektral & K-Means
│   ├── run_evaluation_tuning.py    # Menjalankan tuning parameter K klaster
│   └── run_storytelling.py         # Mengekspor 5 infografis data storytelling utama
├── web_dashboard/                  # Aplikasi Web Dashboard Interaktif & Live Scanner
│   ├── index.html                  # Struktur visual dashboard HTML
│   ├── index.css                   # Desain modern premium (Dark Mode, Glassmorphism)
│   ├── app.js                      # Logika interaktif UMAP Explorer & Live Scanner
│   └── generate_web_data.py        # Pengompres database JSON produk
├── reports/                        # Dokumen Laporan Utama Tugas Akhir
│   ├── Laporan_Gabungan_Data_Storytelling_Halal_Final.docx # File Word Format Baku (TNR 12, Justified)
│   ├── Laporan_Gabungan_Data_Storytelling_Halal.md   # File Markdown Laporan Utama
│   ├── Laporan_Gabungan_Data_Storytelling_Halal.pdf  # File PDF Laporan Utama
│   └── Laporan_Gabungan_Data_Storytelling_Halal.docx # Backup konversi docx standar
├── output_halal/                   # Folder target ekspor 6 infografis data storytelling
├── mca_spectral_plot.png           # Gambar visualisasi UMAP Spektral 2D (Root)
├── kmeans_vs_spectral_comparison.png # Gambar visualisasi komparatif spasial (Root)
├── spectral_k_range_evaluation.png # Gambar visualisasi analisis siku optimasi K (Root)
├── requirements.txt                # Dependensi pustaka Python
└── README.md                       # Dokumentasi repositori (berkas ini)
```

---

## 🛠️ Instalasi & Persiapan Lingkungan

1. **Klon Repositori / Pindah ke Direktori Proyek:**
   Buka terminal/shell dan pastikan Anda berada di direktori repositori:
   ```bash
   cd tugas_akhir_data_storytelling
   ```

2. **Instalasi Pustaka Dependensi:**
   Pasang seluruh pustaka Python yang dibutuhkan melalui berkas `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Dependensi Tambahan (Untuk Otomasi Dokumen Laporan):**
   Jika Anda berniat memodifikasi dan meregenerasi dokumen laporan `.docx` dari `.md` menggunakan automasi naskah kami, pastikan Anda telah memasang **Pandoc** di sistem Anda serta pustaka Python berikut:
   ```bash
   pip install python-docx pypandoc
   ```

---

## 🚀 Panduan Eksekusi Skrip

### 1. Menjalankan Pipeline ETL & Pemodelan dari Awal
Jika Anda ingin mengekstrak data dari data mentah `lodhalalturtle.ttl` (terletak di direktori utama luar) dan melatih ulang model Spektral:
```bash
# Langkah 1: Ekstraksi Data RDF Turtle menjadi Tabular CSV
python scripts/extract_data.py

# Langkah 2: Pemodelan MCA, Spectral Clustering K=8, & K-Means Baseline
python scripts/run_modeling.py
```

### 2. Mengekspor Ulang 5 Infografis Storytelling
Untuk menghasilkan kembali 5 infografis visualisasi utama ke dalam direktori `output_halal/`:
```bash
python scripts/run_storytelling.py
```

### 3. Membuka Web Dashboard Secara Lokal
Aplikasi dashboard web dirancang dengan arsitektur *client-side* murni, yang memuat visualisasi spasial interaktif UMAP 2D dan fitur **Live Scanner** untuk mensimulasikan status kehalalan resep secara instan.
* Buka berkas `web_dashboard/index.html` langsung pada browser web Anda (Google Chrome, Firefox, Safari, dll.).
* Purwarupa ini juga di-deploy secara publik dan dapat diakses langsung secara online melalui tautan: **[halal-analyzer.pages.dev](https://halal-analyzer.pages.dev)**.
