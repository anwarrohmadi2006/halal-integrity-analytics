import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
    normalized_mutual_info_score,
    adjusted_mutual_info_score
)

def cramers_v(contingency_table) -> float:
    """
    Menghitung statistik asosiasi Cramer's V untuk mengukur korelasi klaster dengan kelas luar.
    """
    chi2 = chi2_contingency(contingency_table)[0]
    n_total = contingency_table.sum().sum()
    min_dim = min(contingency_table.shape) - 1
    return np.sqrt(chi2 / (n_total * min_dim)) if min_dim > 0 else 0.0

def calculate_ami_nmi(obj_status: np.ndarray, labels: np.ndarray) -> tuple:
    """
    Menghitung Adjusted Mutual Information (AMI) dan Normalized Mutual Information (NMI).
    """
    ami = adjusted_mutual_info_score(obj_status, labels)
    nmi = normalized_mutual_info_score(obj_status, labels)
    return ami, nmi

def calculate_connectivity_score(X: np.ndarray, labels: np.ndarray, n_neighbors: int = 10) -> float:
    """
    Menghitung persentase tetangga terdekat (KNN) di ruang kontinu yang memiliki label klaster sama.
    """
    nn = NearestNeighbors(n_neighbors=n_neighbors + 1, n_jobs=-1)
    nn.fit(X)
    _, indices = nn.kneighbors(X)
    
    same_label_count = 0
    for i in range(len(X)):
        point_label = labels[i]
        neighbor_labels = labels[indices[i, 1:]]
        same_label_count += np.sum(neighbor_labels == point_label)
        
    return same_label_count / (len(X) * n_neighbors)

def calculate_graph_conductance(A_sym, labels: np.ndarray, n_clusters: int = 8) -> float:
    """
    Menghitung Average Graph Conductance untuk mengukur keterisolasian kelompok graf (semakin rendah semakin baik).
    """
    degrees = np.array(A_sym.sum(axis=1)).flatten()
    total_volume = degrees.sum()
    conductances = []
    
    for cid in range(n_clusters):
        mask = (labels == cid)
        vol_c = degrees[mask].sum()
        internal_weight = A_sym[mask][:, mask].sum()
        cut_c = vol_c - internal_weight
        denom = min(vol_c, total_volume - vol_c)
        cond_c = cut_c / denom if denom > 0 else 0.0
        conductances.append(cond_c)
        
    return np.mean(conductances)

def calculate_euclidean_metrics(X: np.ndarray, labels: np.ndarray, sample_size: int = 3000) -> tuple:
    """
    Menghitung metrik berbasis Euclidean konveks (Silhouette, DBI, CHI) menggunakan subsampel acak.
    """
    n = len(X)
    actual_sample_size = min(sample_size, n)
    
    rng = np.random.RandomState(42)
    sample_indices = rng.choice(n, size=actual_sample_size, replace=False)
    
    X_sample = X[sample_indices]
    labels_sample = labels[sample_indices]
    
    sil = silhouette_score(X_sample, labels_sample, metric='euclidean')
    dbi = davies_bouldin_score(X_sample, labels_sample)
    chi = calinski_harabasz_score(X_sample, labels_sample)
    
    return sil, dbi, chi
