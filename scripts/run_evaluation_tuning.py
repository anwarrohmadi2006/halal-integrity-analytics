import os
import sys
import time
import pandas as pd
import numpy as np
import gc
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.neighbors import kneighbors_graph
import matplotlib.pyplot as plt

# Tambahkan folder root final_project ke sys.path untuk impor modular
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.classifier import load_halal_status_dict, classify_product
from src.modeling import (
    prepare_binary_matrix,
    run_mca,
    build_sparse_knn_graph,
    run_umap_projection
)
from src.evaluation import (
    cramers_v,
    calculate_graph_conductance,
    calculate_euclidean_metrics
)
from src.visualization import (
    plot_kmeans_vs_spectral
)

def main():
    print("=== PIPELINE EVALUASI & TUNING MODEL ===")
    
    # 1. Load data utama
    input_csv = os.path.join("data", "processed", "halal_products_tabular.csv")
    if not os.path.exists(input_csv):
        input_csv = "halal_products_tabular.csv"
        if not os.path.exists(input_csv):
            print("ERROR: File halal_products_tabular.csv tidak ditemukan. Jalankan scripts/extract_data.py.")
            sys.exit(1)
            
    df = pd.read_csv(input_csv)
    df_has_ing = df[df['ingredients'].fillna('') != ''].copy().reset_index(drop=True)
    n_products = len(df_has_ing)
    
    # 2. Klasifikasi Status Halal Objektif
    status_dict = load_halal_status_dict()
    df_has_ing['obj_status'] = df_has_ing['ingredients'].apply(lambda x: classify_product(x, status_dict))
    obj_status = df_has_ing['obj_status'].values
    
    # 3. Buat Matriks Biner & Jalankan MCA
    df_binary, _ = prepare_binary_matrix(df_has_ing, top_n=500)
    X_mca = run_mca(df_binary, n_components=8)
    
    del df_binary
    gc.collect()
    
    # 4. Bangun Graf KNN
    A_sym = build_sparse_knn_graph(X_mca, n_neighbors=100, gamma=0.1)
    
    # ==========================================
    # BAGIAN A: PERBANDINGAN K-MEANS VS SPECTRAL
    # ==========================================
    print("\n--- A. Perbandingan Spasial K-Means vs. Spectral ---")
    km = KMeans(n_clusters=8, random_state=42, n_init=10)
    km_labels = km.fit_predict(X_mca)
    
    sc = SpectralClustering(
        n_clusters=8,
        affinity='precomputed',
        eigen_solver='lobpcg',
        assign_labels='discretize',
        random_state=42,
        n_jobs=-1
    )
    sc_labels = sc.fit_predict(A_sym)
    
    # Jalankan UMAP & Visualisasikan perbandingan
    umap_coords = run_umap_projection(X_mca)
    plot_kmeans_vs_spectral(umap_coords, km_labels, sc_labels, save_path="kmeans_vs_spectral_comparison.png")
    print("Grafik perbandingan kmeans_vs_spectral_comparison.png berhasil diekspor.")
    
    # ==========================================
    # BAGIAN B: OPTIMASI K CLUSTER (K = 2 s.d 13)
    # ==========================================
    print("\n--- B. Uji Optimasi Jumlah Klaster (K = 2 s.d. 13) ---")
    # Sub-sampel untuk metrik Euclidean agar hemat waktu & memori
    sample_size = min(3000, n_products)
    rng = np.random.RandomState(42)
    sample_indices = rng.choice(n_products, size=sample_size, replace=False)
    X_sample = X_mca[sample_indices]
    
    results = []
    k_range = range(2, 14)
    for k in k_range:
        t_start = time.time()
        sc_k = SpectralClustering(
            n_clusters=k,
            affinity='precomputed',
            eigen_solver='lobpcg',
            assign_labels='discretize',
            random_state=42,
            n_jobs=-1
        )
        try:
            lbls = sc_k.fit_predict(A_sym)
            duration = time.time() - t_start
            
            # Hitung metrik
            counts = pd.Series(lbls).value_counts()
            min_s = int(counts.min())
            max_s = int(counts.max())
            
            sil, dbi, _ = calculate_euclidean_metrics(X_mca, lbls, sample_size=3000)
            cond = calculate_graph_conductance(A_sym, lbls, n_clusters=k)
            
            ct = pd.crosstab(lbls, obj_status)
            cv = cramers_v(ct)
            
            print(f"  K = {k:02d} | Sil: {sil:.4f} | Cond: {cond:.4f} | Cramer's V: {cv:.4f} | Min/Max: [{min_s}/{max_s}]")
            results.append({
                'K': k,
                'Silhouette_Score': sil,
                'Davies_Bouldin_Index': dbi,
                'Average_Conductance': cond,
                'Cramers_V': cv,
                'Min_Cluster_Size': min_s,
                'Max_Cluster_Size': max_s,
                'Time_Seconds': duration
            })
        except Exception as e:
            print(f"  Gagal pada K={k}: {e}")
            
    # Simpan hasil optimasi K
    df_res = pd.DataFrame(results)
    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    df_res.to_csv(os.path.join("data", "processed", "spectral_k_range_results.csv"), index=False)
    
    # Buat plot optimasi K
    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=150)
    color = '#1D3557' # Navy
    ax1.set_xlabel('Number of Clusters (K)', fontsize=11, fontweight='bold')
    ax1.set_ylabel("Cramer's V (Halal Correlation)", color=color, fontsize=11, fontweight='bold')
    ax1.plot(df_res['K'], df_res['Cramers_V'], marker='o', color=color, linewidth=2.5, label="Cramer's V")
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.3)
    
    ax2 = ax1.twinx()
    color = '#E63946' # Red
    ax2.set_ylabel('Average Graph Conductance (Lower is Better)', color=color, fontsize=11, fontweight='bold')
    ax2.plot(df_res['K'], df_res['Average_Conductance'], marker='s', color=color, linewidth=2.5, linestyle='--', label="Conductance")
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title("Spectral Clustering K Optimization (K=2 to 13)", fontsize=13, fontweight='bold', pad=15)
    fig.tight_layout()
    plt.savefig("spectral_k_range_evaluation.png")
    plt.close()
    print("Grafik optimasi spectral_k_range_evaluation.png berhasil diekspor.")
    


if __name__ == "__main__":
    main()
