# Workspace Tugas Akhir: Data Storytelling (Sains Data)
**Navigasi Titik Kritis Halal: Visualisasi Pola Formulasi & Asosiasi Bahan Pangan Komersial**

Workspace ini didedikasikan untuk pengerjaan proyek akhir mata kuliah **Data Storytelling / Python untuk Sains Data**. Proyek ini bertujuan untuk memetakan dan menceritakan pola formulasi bahan baku pangan komersial di Indonesia, mendeteksi potensi risiko bahan kritis syubhat (CCP), serta menyajikan data secara interaktif bagi konsumen dan industri.

---

## 🎨 Fokus Laporan & Narasi Visual

Proyek ini tidak hanya melakukan pemodelan matematika, melainkan menyajikan cerita data (*data story*) melalui **4 infografis visual** terintegrasi:

1.  **Gambar 1: Dashboard Overview (`fig1_dashboard_overview.png`)**
    *   *Insight*: Ringkasan statistik ekosistem data (termasuk visualisasi kesenjangan data bahan baku antara produk bersertifikat vs non-sertifikat).
2.  **Gambar 2: Analisis Bahan Bermasalah (`fig2_bahan_bermasalah.png`)**
    *   *Insight*: Menyoroti **Gelatin** sebagai bahan aditif syubhat (mushbooh) paling dominan di pasaran komersial (muncul 620 kali).
3.  **Gambar 3: Heatmap Ko-kemunculan Bahan (`fig3_cooccurrence_heatmap.png`)**
    *   *Insight*: Memetakan pola pasangan aditif yang paling sering dicampurkan bersama dalam formulasi resep industri pangan (seperti Garam + Air, dan Perisa + Gula Dextrose).
4.  **Gambar 4: Karakteristik Kluster Pangan (`fig4_cluster.png`)**
    *   *Insight*: Membuktikan secara empiris bahwa **semakin banyak jumlah bahan aditif dalam resep (kompleksitas), tingkat kehalalan objektif produk cenderung menurun** karena akumulasi risiko bahan kritis.


---

## 📂 Peta Folder Workspace

Struktur folder dirancang modular dan mandiri (isolated bundle) untuk mempermudah pengumpulan tugas akhir:

```text
tugas_akhir_data_storytelling/
├── data/
│   └── processed/                  # File CSV olahan hasil pemodelan
├── src/                            # Modul visualisasi & parser python
├── scripts/                        # Skrip CLI untuk eksekusi visualisasi
│   ├── run_storytelling.py         # Skrip utama penghasil infografis visual
│   └── run_modeling.py             # Skrip pemodelan spektral backend
├── web_dashboard/                  # Aplikasi Web Dashboard Interaktif & Live Scanner
│   ├── index.html                  # Aplikasi web dashboard
│   └── data/                       # Database Msgpack/JSON terkompresi
├── reports/                        # LAPORAN UTAMA TUGAS AKHIR
│   ├── Laporan_Gabungan_Data_Storytelling_Halal.docx # Laporan format Word
│   ├── Laporan_Gabungan_Data_Storytelling_Halal.pdf  # Laporan format PDF
│   └── Laporan_Gabungan_Data_Storytelling_Halal.md   # Laporan format Markdown
└── output_halal/                   # Folder hasil ekspor 4 gambar infografis
```

---

## ⚡ Petunjuk Cepat Penggunaan Skrip

### 1. Menghasilkan Gambar Infografis
Untuk meregenerasi atau mengekspor 4 gambar infografis visual di atas ke dalam folder `output_halal/`, jalankan perintah berikut dari folder ini:
```bash
python scripts/run_storytelling.py
```

### 2. Membuka Dashboard Interaktif Web
Dashboard Web dilengkapi fitur **Live Halal Ingredient Scanner** yang ramah pengguna. Anda dapat mengetikkan komposisi bahan baku makanan untuk mendeteksi risiko CCP secara instan.
*   Buka file `web_dashboard/index.html` menggunakan browser Anda untuk memulai demo dashboard interaktif.
