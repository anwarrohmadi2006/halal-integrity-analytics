import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

# Set global matplotlib parameters
matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["axes.unicode_minus"] = False

# Halal Color Palette
PALETTE = {
    "halal":    "#2E8B57", # Sea Green
    "haram":    "#C0392B", # Red
    "mashbooh": "#E67E22", # Orange
    "accent":   "#F1C40F", # Yellow
    "bg":       "#FAFAF8", # Ivory Light
    "text":     "#2C3E50", # Dark Slate
}
CLUSTER_COLORS = ["#E63946", "#2D6A4F", "#457B9D", "#1D3557", "#52B788", "#370617", "#FFB703", "#8338EC"]

def plot_scree_plot(mca_eigenvalues, save_path="mca_scree_plot.png"):
    """
    Memvisualisasikan Scree Plot nilai eigen MCA beserta batas kritis Kaiser.
    """
    plt.figure(figsize=(9, 5), dpi=150)
    plt.plot(range(1, len(mca_eigenvalues) + 1), mca_eigenvalues, 'o-', linewidth=2, color=PALETTE["text"])
    plt.axhline(y=1.0, color='r', linestyle='--', label='Kaiser Criterion (Eigenvalue = 1.0)')
    plt.title("MCA Scree Plot (Eigenvalue Distribution)", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Principal Components", fontsize=10)
    plt.ylabel("Eigenvalue (Inertia)", fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_umap_clusters(umap_coords, labels, cluster_labels, save_path="mca_spectral_plot.png"):
    """
    Memvisualisasikan hasil Spectral Clustering pada UMAP 2D space.
    """
    plt.figure(figsize=(12, 9), dpi=150)
    n_clusters = len(np.unique(labels))
    
    for cluster_idx in range(n_clusters):
        cluster_mask = (labels == cluster_idx)
        label_text = cluster_labels.get(cluster_idx + 1, f"Cluster {cluster_idx + 1}")
        plt.scatter(
            umap_coords[cluster_mask, 0],
            umap_coords[cluster_mask, 1],
            label=f"{label_text} (N={cluster_mask.sum()})",
            alpha=0.8,
            edgecolors='none',
            s=30,
            c=CLUSTER_COLORS[cluster_idx]
        )
        
    plt.title("UMAP 2D Projection (MCA + Sparse RBF Spectral Clustering)", fontsize=15, fontweight='bold', pad=20)
    plt.xlabel("UMAP Dimension 1", fontsize=11, fontweight='bold')
    plt.ylabel("UMAP Dimension 2", fontsize=11, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(loc='best', frameon=True, shadow=True, facecolor='white', edgecolor='none', fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_kmeans_vs_spectral(umap_coords, km_labels, sc_labels, save_path="kmeans_vs_spectral_comparison.png"):
    """
    Membandingkan struktur spasial linear K-Means (Euclidean cuts) vs Spectral (Topologi graf) pada UMAP space.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=150)
    
    # 1. K-Means
    for i in range(8):
        mask = (km_labels == i)
        ax1.scatter(umap_coords[mask, 0], umap_coords[mask, 1], s=10, alpha=0.7, label=f"C{i+1} (N={mask.sum()})")
    ax1.set_title("K-Means Clustering baseline (Euclidean Spherical Cuts)\nMenumpuk data di pusat klaster", fontsize=12, fontweight='bold')
    ax1.set_xlabel("UMAP 1")
    ax1.set_ylabel("UMAP 2")
    ax1.grid(True, linestyle='--', alpha=0.3)
    ax1.legend(loc='lower left', fontsize=8)
    
    # 2. Spectral Clustering
    for i in range(8):
        mask = (sc_labels == i)
        ax2.scatter(umap_coords[mask, 0], umap_coords[mask, 1], s=10, alpha=0.7, label=f"C{i+1} (N={mask.sum()})")
    ax2.set_title("Spectral Clustering (Graph connectivity & local density)\nMengikuti struktur manifold alami", fontsize=12, fontweight='bold')
    ax2.set_xlabel("UMAP 1")
    ax2.set_ylabel("UMAP 2")
    ax2.grid(True, linestyle='--', alpha=0.3)
    ax2.legend(loc='lower left', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_synthetic_spiral_comparison(X, km_labels, sc_labels, save_path="synthetic_spiral_comparison.png"):
    """
    Memvisualisasikan performa pemisahan data non-konveks spiral K-Means vs Spectral.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=150)
    
    # K-Means
    ax1.scatter(X[:, 0], X[:, 1], c=km_labels, cmap='rainbow', s=15, alpha=0.8)
    ax1.set_title("K-Means Clustering baseline\n(Gagal memisahkan spiral karena Voronoi cut linear)", fontsize=11, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.3)
    
    # Spectral
    ax2.scatter(X[:, 0], X[:, 1], c=sc_labels, cmap='rainbow', s=15, alpha=0.8)
    ax2.set_title("Spectral Clustering\n(Berhasil memisahkan spiral berdasarkan konektivitas graf)", fontsize=11, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_data_storytelling_dashboard(df_ingredients, df_cert, df_cooc, df_clusters, df_nutrition, save_dir="output_halal"):
    """
    Membuat 5 grafik infografis data storytelling terpadu dan menyimpannya ke folder output.
    """
    os.makedirs(save_dir, exist_ok=True)
    palette_colors = ["#2E8B57", "#27AE60", "#F39C12", "#E74C3C", "#8E44AD", "#2980B9", "#16A085", "#D35400"]

    # 1. FIG 1: DASHBOARD OVERVIEW
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.patch.set_facecolor(PALETTE["bg"])
    fig.suptitle("PETA RISIKO TITIK KRITIS HALAL (CCP)\nData Storytelling Pangan Komersial",
                 fontsize=16, fontweight="bold", color=PALETTE["text"], y=0.98)

    # Pie status bahan
    status_counts = df_ingredients["halal_status"].value_counts()
    ax = axes[0, 0]
    ax.set_facecolor(PALETTE["bg"])
    sizes = [status_counts.get(s, 0) for s in ["halal","mashbooh","haram"]]
    labels_p = [f"Halal\n({sizes[0]} bahan)", f"Mushbooh\n({sizes[1]} bahan)", f"Haram\n({sizes[2]} bahan)"]
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels_p,
        colors=[PALETTE["halal"],PALETTE["mashbooh"],PALETTE["haram"]],
        autopct="%1.1f%%", startangle=90,
        wedgeprops=dict(edgecolor="white", linewidth=2),
        textprops=dict(color=PALETTE["text"], fontsize=9))
    for at in autotexts:
        at.set_fontsize(10); at.set_fontweight("bold"); at.set_color("white")
    ax.set_title("Status Bahan Baku Halal", fontweight="bold", color=PALETTE["text"], pad=10)

    # Volume data
    ax = axes[0, 1]
    ax.set_facecolor(PALETTE["bg"])
    cats = ["Total\nProduk", "Ada\nBahan", "Tanpa\nBahan", "Manufaktur\nUnik"]
    vals = [59453, 15739, 43714, 2521]
    bars = ax.barh(cats, vals, color=[palette_colors[1], palette_colors[0], palette_colors[3], palette_colors[5]],
                   edgecolor="white", linewidth=1.5, height=0.55)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_width()+200, bar.get_y()+bar.get_height()/2,
                f"{val:,}", va="center", ha="left", fontsize=9, fontweight="bold", color=PALETTE["text"])
    ax.set_xlim(0, 68000)
    ax.set_title("Volume Data LOD Halal", fontweight="bold")
    ax.spines[["top","right","bottom"]].set_visible(False)

    # Kelengkapan per sertifikasi
    ax = axes[0, 2]
    ax.set_facecolor(PALETTE["bg"])
    x = np.arange(len(df_cert))
    w = 0.35
    ax.bar(x-w/2, df_cert["tanpa_bahan"], w, label="Tanpa Bahan", color=PALETTE["haram"], alpha=0.85)
    ax.bar(x+w/2, df_cert["dengan_bahan"], w, label="Dengan Bahan", color=PALETTE["halal"], alpha=0.85)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(df_cert["status"])
    ax.set_title("Ketersediaan Bahan per Sertifikasi", fontweight="bold")
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.3)

    # Top 12 Bahan
    ax = axes[1, 0]
    ax.set_facecolor(PALETTE["bg"])
    top_12 = df_ingredients.sort_values(by="frequency_in_products", ascending=False).head(12)
    bars = ax.barh(top_12["ingredient_name"], top_12["frequency_in_products"], color="#34495E")
    for bar in bars:
        ax.text(bar.get_width()+100, bar.get_y()+bar.get_height()/2,
                f"{int(bar.get_width()):,}", va="center", ha="left", fontsize=8, color=PALETTE["text"])
    ax.set_title("12 Bahan Baku Terpopuler", fontweight="bold")
    ax.spines[["top","right","bottom"]].set_visible(False)

    # Sparsity Nutrisi
    ax = axes[1, 1]
    ax.set_facecolor(PALETTE["bg"])
    bars = ax.bar(df_nutrition["nutrisi"], df_nutrition["pct_non_zero"]*100, color="#16A085", width=0.5)
    for bar in bars:
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                f"{bar.get_height():.2f}%", ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax.set_ylim(0, 30)
    ax.set_ylabel("Persentase Keterisian (%)")
    ax.set_title("Sparsity Fitur Gizi (Data Terisi)", fontweight="bold")
    ax.spines[["top","right"]].set_visible(False)

    # Risk level per status
    ax = axes[1, 2]
    ax.set_facecolor(PALETTE["bg"])
    pivot_risk = pd.DataFrame({
        "low": [42, 6, 0],
        "medium": [1, 2, 0],
        "high": [0, 6, 3]
    }, index=["halal", "mashbooh", "haram"])
    pivot_risk.plot(kind="bar", stacked=True, color=["#2ECC71","#F39C12","#E74C3C"], ax=ax, width=0.5)
    ax.set_title("Distribusi Tingkat Risiko Bahan", fontweight="bold")
    ax.set_xlabel("Status Halal")
    ax.set_ylabel("Jumlah Bahan")
    ax.legend(title="Tingkat Risiko")
    ax.grid(True, linestyle=":", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "fig1_dashboard_overview.png"))
    plt.close()

    # 2. FIG 2: BAHAN BERMASALAH (MUSHBOOH & HARAM)
    plt.figure(figsize=(10, 6), dpi=150)
    plt.gca().set_facecolor(PALETTE["bg"])
    bad_ings = df_ingredients[df_ingredients["halal_status"].isin(["mashbooh", "haram"])].sort_values(by="frequency_in_products", ascending=False)
    colors_bad = bad_ings["halal_status"].map({"mashbooh": PALETTE["mashbooh"], "haram": PALETTE["haram"]})
    bars = plt.barh(bad_ings["ingredient_name"].head(10), bad_ings["frequency_in_products"].head(10), color=colors_bad.head(10))
    for bar in bars:
        plt.text(bar.get_width()+10, bar.get_y()+bar.get_height()/2,
                 f"{int(bar.get_width()):,} prod", va="center", ha="left", fontsize=9, fontweight="bold")
    plt.title("Top 10 Bahan Baku Syubhat (Orange) & Haram (Merah)\nMenyoroti Gelatin sebagai Titik Kritis Utama (CCP)", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Frekuensi Penggunaan dalam Produk Pangan")
    plt.gca().spines[["top","right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "fig2_bahan_bermasalah.png"))
    plt.close()

    # 3. FIG 3: CO-OCCURRENCE HEATMAP
    plt.figure(figsize=(10, 8), dpi=150)
    cmap = LinearSegmentedColormap.from_list("custom_green", [PALETTE["bg"], PALETTE["halal"]])
    sns.heatmap(df_cooc, annot=True, fmt="d", cmap=cmap, cbar=True, square=True,
                linewidths=.5, annot_kws={"size": 9, "weight": "bold", "color": PALETTE["text"]})
    plt.title("Heatmap Pola Ko-kemunculan Bahan Baku Pangan Komersial\n(Mendeteksi Asosiasi Formulasi Resep Industri)", fontsize=13, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "fig3_cooccurrence_heatmap.png"))
    plt.close()

    # 4. FIG 4: CLUSTERS CHARACTERISTICS
    plt.figure(figsize=(10, 6), dpi=150)
    plt.gca().set_facecolor(PALETTE["bg"])
    scatter = plt.scatter(
        df_clusters["avg_ingredients"], df_clusters["halal_pct"],
        s=df_clusters["n_products"] * 0.7, c=df_clusters["halal_pct"],
        cmap="RdYlGn", alpha=0.85, edgecolors="#2C3E50", linewidths=1.5
    )
    for i, row in df_clusters.iterrows():
        plt.text(row["avg_ingredients"], row["halal_pct"] + 0.9,
                 f"{row['cluster_label']}\n({row['n_products']} prod)",
                 ha="center", fontsize=8, fontweight="bold", color=PALETTE["text"])
    plt.title("Karakterisasi Kluster Produk Pangan Spektral\nHubungan Kompleksitas Bahan Baku vs Kehalalan Objektif", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Rata-rata Jumlah Bahan Tambahan per Produk", fontweight="bold")
    plt.ylabel("Tingkat Kehalalan Objektif (%)", fontweight="bold")
    plt.ylim(78, 103)
    plt.xlim(1.5, 12.5)
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "fig4_cluster.png"))
    plt.close()

    # 5. FIG 5: INSIGHT SUMMARY
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=150)
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])
    ax.axis("off")
    
    plt.text(0.5, 0.92, "RINGKASAN TEMUAN UTAMA (KEY INSIGHTS)\nINTEGRITAS HALAL PANGAN KOMERSIAL",
             fontsize=15, fontweight="bold", color=PALETTE["text"], ha="center", va="center")
             
    insights = [
        ("1. Celah Transparansi (Sparsity Bias)", 
         "Sebesar 73.53% data produk tidak memiliki data bahan baku di database sekunder LOD Halal,\ndan 99.9% produk dengan sertifikat aktif tidak mencantumkan komposisi bahan bakunya. Hal ini membatasi\naudit digital berbasis bahan baku secara menyeluruh."),
        ("2. Gelatin Sebagai Titik Kritis Terbesar", 
         "Gelatin (Syubhat/Mushbooh) muncul sebanyak 620 kali pada produk pangan komersial.\nGelatin adalah titik kritis utama karena di pasar dunia sering kali diekstrak dari kulit/tulang babi\natau hewan non-halal."),
        ("3. Kompleksitas Resep vs Kehalalan", 
         "Semakin kompleks bahan tambahan pangan (aditif) yang digunakan, semakin turun tingkat kehalalannya.\nKlaster resep kompleks (C8) memiliki tingkat kehalalan terendah (82.6%) dibanding resep sederhana (C7: 99.4%)."),
        ("4. Pola Formulasi Resep Industri", 
         "Hasil heatmap menunjukkan asosiasi resep yang sangat konsisten, seperti perisa komersial\nyang selalu berpasangan dengan gula pengikat rasa (dextrose) pada klaster olahan daging."),
        ("5. Pentingnya Pemodelan Non-Linier Graf", 
         "Uji metrik membuktikan model Spektral Graf jauh lebih representatif memetakan biokimia pangan\n(Conductance = 0.0935) dibanding model linier K-Means yang memaksakan pengelompokan membulat (Voronoi)."),
        ("6. Sistem Pendukung Keputusan", 
         "Hasil pemetaan 8 klaster biokimia ini sangat direkomendasikan sebagai asisten digital (Decision Support)\nbagi lembaga audit pangan halal untuk mendeteksi potensi risiko kontaminasi secara dini.")
    ]
    
    positions = [
        (0.05, 0.65), (0.52, 0.65),
        (0.05, 0.38), (0.52, 0.38),
        (0.05, 0.11), (0.52, 0.11)
    ]
    
    for (title, text), (px, py) in zip(insights, positions):
        # Draw box
        rect = mpatches.FancyBboxPatch(
            (px, py), 0.43, 0.22,
            boxstyle="round,pad=0.01",
            facecolor="white", edgecolor="#BDC3C7", linewidth=1.2,
            mutation_scale=0.02
        )
        ax.add_patch(rect)
        
        # Add text
        plt.text(px + 0.02, py + 0.18, title, fontsize=10, fontweight="bold", color="#2C3E50", ha="left", va="center")
        plt.text(px + 0.02, py + 0.09, text, fontsize=7.5, color="#555555", ha="left", va="center", linespacing=1.4)
        
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "fig5_insight_summary.png"))
    plt.close()
    print(f"5 Grafik Infografis Storytelling berhasil disimpan ke: {save_dir}/")
