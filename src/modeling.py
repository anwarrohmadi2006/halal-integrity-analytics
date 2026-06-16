import time
import pandas as pd
import numpy as np
import prince
import umap
from sklearn.cluster import SpectralClustering, KMeans
from sklearn.neighbors import kneighbors_graph

def prepare_binary_matrix(df_has_ing: pd.DataFrame, top_n: int = 500) -> tuple:
    """
    Ekstrak top_n bahan aditif terpopuler dan buat matriks indikator biner (sparse matrix).
    """
    print(f"Mengekstrak top {top_n} bahan aditif pangan...")
    all_ings = []
    for ing_str in df_has_ing['ingredients'].fillna(''):
        ings = [i.strip().lower() for i in str(ing_str).split(',') if i.strip()]
        all_ings.extend(ings)
        
    ing_series = pd.Series(all_ings)
    top_ingredients = ing_series.value_counts().head(top_n).index.tolist()
    
    print("Membangun matriks biner indikator...")
    data_dict = {}
    for ing in top_ingredients:
        # Menghindari karakter khusus pada nama kolom
        col_name = f"ing_{ing[:40].replace(' ', '_').replace('.', '').replace('/', '_')}"
        data_dict[col_name] = df_has_ing['ingredients'].apply(lambda x: "1" if ing in str(x).lower() else "0")
        
    return pd.DataFrame(data_dict), top_ingredients

def run_mca(df_binary: pd.DataFrame, n_components: int = 8) -> np.ndarray:
    """
    Menjalankan reduksi dimensi Multiple Correspondence Analysis (MCA) pada ruang biner.
    """
    print(f"Menjalankan analisis multivariat MCA (komponen={n_components})...")
    t0 = time.time()
    mca = prince.MCA(n_components=n_components, random_state=42)
    X_mca = mca.fit_transform(df_binary).values
    print(f"MCA selesai dalam {time.time() - t0:.2f} detik.")
    return X_mca

def build_sparse_knn_graph(X: np.ndarray, n_neighbors: int = 100, gamma: float = 0.1):
    """
    Membangun graf ketetanggaan Sparse KNN dan menerapkan kernel RBF.
    """
    print(f"Mengonstruksi graf ketetanggaan Sparse KNN (n_neighbors={n_neighbors})...")
    t0 = time.time()
    A = kneighbors_graph(X, n_neighbors=n_neighbors, mode='distance', include_self=True, n_jobs=-1)
    
    # Konversi jarak Euclidean ke kemiripan RBF: exp(-gamma * dist^2)
    A.data = np.exp(-gamma * (A.data ** 2))
    
    # Simetrisasi matriks bobot graf
    A_sym = 0.5 * (A + A.T)
    print(f"Graf selesai dibangun dalam {time.time() - t0:.2f} detik.")
    return A_sym

def run_spectral_clustering(A_sym, n_clusters: int = 8) -> np.ndarray:
    """
    Melakukan segmentasi klaster berbasis spektral graf menggunakan solver LOBPCG.
    """
    print(f"Menjalankan Spectral Clustering (K={n_clusters}) pada graf...")
    t0 = time.time()
    sc = SpectralClustering(
        n_clusters=n_clusters,
        affinity='precomputed',
        eigen_solver='lobpcg',
        assign_labels='discretize',
        random_state=42,
        n_jobs=-1
    )
    labels = sc.fit_predict(A_sym)
    print(f"Spectral Clustering selesai dalam {time.time() - t0:.2f} detik.")
    return labels

def run_kmeans(X: np.ndarray, n_clusters: int = 8) -> np.ndarray:
    """
    Melakukan baseline clustering K-Means pada ruang kontinu.
    """
    print(f"Menjalankan K-Means Clustering baseline (K={n_clusters})...")
    t0 = time.time()
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    print(f"K-Means selesai dalam {time.time() - t0:.2f} detik.")
    return labels

def run_umap_projection(X: np.ndarray, n_components: int = 2, n_neighbors: int = 15, min_dist: float = 0.15) -> np.ndarray:
    """
    Memproyeksikan koordinat dimensi tinggi ke ruang visualisasi 2D menggunakan UMAP.
    """
    print("Menjalankan proyeksi reduksi dimensi non-linier UMAP...")
    t0 = time.time()
    reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, n_components=n_components, metric='euclidean', random_state=42)
    umap_coords = reducer.fit_transform(X)
    print(f"UMAP selesai dalam {time.time() - t0:.2f} detik.")
    return umap_coords
