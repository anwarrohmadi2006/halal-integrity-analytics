import os
import sys
import time
import pandas as pd
import numpy as np

# Tambahkan folder root final_project ke sys.path untuk impor modular
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.classifier import load_halal_status_dict, classify_product
from src.modeling import (
    prepare_binary_matrix,
    run_mca,
    build_sparse_knn_graph,
    run_spectral_clustering,
    run_umap_projection
)
from src.evaluation import (
    cramers_v,
    calculate_ami_nmi,
    calculate_connectivity_score,
    calculate_graph_conductance,
    calculate_euclidean_metrics
)
from src.visualization import plot_umap_clusters

def main():
    print("=== PIPELINE PEMODELAN MULTIVARIAT (MCA + SPECTRAL CLUSTERING) ===")
    
    # Jalur file input/output
    input_csv = os.path.join("data", "processed", "halal_products_tabular.csv")
    if not os.path.exists(input_csv):
        # Fallback jika dijalankan dari root langsung
        input_csv = "halal_products_tabular.csv"
        if not os.path.exists(input_csv):
            print(f"ERROR: File '{input_csv}' tidak ditemukan. Silakan jalankan scripts/extract_data.py terlebih dahulu.")
            sys.exit(1)
            
    print(f"Memuat data dari: {input_csv}")
    df = pd.read_csv(input_csv)
    
    # Filter produk yang memiliki komposisi bahan
    df_has_ing = df[df['ingredients'].fillna('') != ''].copy().reset_index(drop=True)
    n_products = len(df_has_ing)
    print(f"Total produk dengan komposisi: {n_products}")
    
    # 1. Melakukan klasifikasi status halal objektif (Worst-case) [CRISP-DM: Data Preparation]
    status_dict = load_halal_status_dict()
    df_has_ing['obj_status'] = df_has_ing['ingredients'].apply(lambda x: classify_product(x, status_dict))
    obj_status = df_has_ing['obj_status'].values
    
    # 2. Membangun matriks biner untuk bahan baku [CRISP-DM: Data Preparation]
    df_binary, top_ingredients = prepare_binary_matrix(df_has_ing, top_n=500)
    
    # 3. Mereduksi dimensi menggunakan MCA [CRISP-DM: Modeling]
    X_mca = run_mca(df_binary, n_components=8)
    
    # 4. Mengkonstruksi graf ketetanggaan KNN [CRISP-DM: Modeling]
    A_sym = build_sparse_knn_graph(X_mca, n_neighbors=100, gamma=0.1)
    
    # 5. Menjalankan segmentasi klaster berbasis spektral [CRISP-DM: Modeling]
    labels = run_spectral_clustering(A_sym, n_clusters=8)
    df_has_ing['cluster'] = labels
    
    # 6. Memproyeksikan tata letak spasial ke 2D menggunakan UMAP [CRISP-DM: Modeling]
    umap_coords = run_umap_projection(X_mca, n_components=2, n_neighbors=15, min_dist=0.15)
    df_has_ing['umap_1'] = umap_coords[:, 0]
    df_has_ing['umap_2'] = umap_coords[:, 1]
    
    # 7. Menyimpan hasil pemodelan ke dalam file CSV [CRISP-DM: Evaluation]
    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    output_csv = os.path.join("data", "processed", "product_spectral_clusters.csv")
    cols_to_save = ['product_id', 'label', 'manufacturer', 'certificate_status', 'ingredients', 'cluster', 'umap_1', 'umap_2']
    df_has_ing[cols_to_save].to_csv(output_csv, index=False)
    print(f"Hasil clustering berhasil disimpan ke: {output_csv}")
    
    # 8. Memvisualisasikan sebaran spasial UMAP [CRISP-DM: Evaluation]
    cluster_labels = {
        1: "Klaster 1: Bumbu Penyedap, Sup Instan, & Olahan Gurih Berdaging",
        2: "Klaster 2: Makanan Ringan, Sayur Awetan, & Produk Biji-bijian",
        3: "Klaster 3: Jus Buah Alami, Smoothies, & Makanan Bayi Organik",
        4: "Klaster 4: Produk Olahan Tepung Terigu & Sereal Terfortifikasi",
        5: "Klaster 5: Saus Buah (Applesauce), Awetan Buah, & Produk Pemanis Buah",
        6: "Klaster 6: Daging Sapi Segar & Olahan Daging Sapi Murni",
        7: "Klaster 7: Produk Komoditas Pertanian Mentah & Minuman Alami",
        8: "Klaster 8: Produk Permen (Confectionery), Roti Manis, & Olahan Susu/Cokelat"
    }
    plot_umap_clusters(umap_coords, labels, cluster_labels, save_path="mca_spectral_plot.png")
    
    # 9. Mengevaluasi performa klastering menggunakan metrik kuantitatif [CRISP-DM: Evaluation]
    print("\nMenghitung metrik performa...")
    connectivity = calculate_connectivity_score(X_mca, labels, n_neighbors=10)
    conductance = calculate_graph_conductance(A_sym, labels, n_clusters=8)
    ami, nmi = calculate_ami_nmi(obj_status, labels)
    
    # Hitung metrik Euclidean (subsampel 3000)
    sil, dbi, chi = calculate_euclidean_metrics(X_mca, labels, sample_size=3000)
    
    # Hitung Cramer's V
    ct = pd.crosstab(labels, obj_status)
    cv = cramers_v(ct)
    
    print("\n=== HASIL EVALUASI PEMODELAN SPEKTRAL ===")
    print(f"1. 10-NN Connectivity Score      : {connectivity:.4f} (Tinggi lebih baik)")
    print(f"2. Average Graph Conductance     : {conductance:.4f} (Rendah lebih baik)")
    print(f"3. Cramer's V (Korelasi Halal)   : {cv:.4f} (Tinggi lebih baik)")
    print(f"4. Adjusted Mutual Info (AMI)    : {ami:.4f} (Tinggi lebih baik)")
    print(f"5. Normalized Mutual Info (NMI)  : {nmi:.4f} (Tinggi lebih baik)")
    print(f"6. Silhouette Score (Euclidean)  : {sil:.4f} (Bias geometris linier)")
    print(f"7. Davies-Bouldin Index (DBI)    : {dbi:.4f} (Bias geometris linier)")
    print(f"8. Calinski-Harabasz Index (CHI) : {chi:.1f} (Bias geometris linier)")

if __name__ == "__main__":
    main()
