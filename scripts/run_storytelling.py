import os
import sys
import numpy as np
import pandas as pd

# Tambahkan folder root final_project ke sys.path untuk impor modular
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visualization import plot_data_storytelling_dashboard

def main():
    print("=== PIPELINE EKSPOR VISUALISASI DATA STORYTELLING ===")
    
    # 1. Mendeklarasikan struktur data agregat untuk storytelling [CRISP-DM: Deployment]
    df_ingredients = pd.DataFrame({
        "ingredient_name": [
            "salt","water","sugar","beef","spice","citric_acid","apple","flavouring",
            "antioxidant","dextrose","vinegar","starch","palm_oil","soy_protein",
            "gelatin","carmine","lard","lecithin","ascorbic_acid","sodium_benzoate",
            "glucose","maltodextrin","natural_flavour","artificial_flavour",
            "monoglyceride","diglyceride","pectin","agar","carrageenan","xanthan_gum",
            "yeast","milk_powder","egg","wheat_flour","corn_starch","potato_starch",
            "cocoa","vanilla","pepper","garlic","onion","tomato","chicken","fish",
            "shrimp","pork","alcohol","lactic_acid","acetic_acid","caramel"
        ],
        "halal_status": [
            "halal","halal","halal","mashbooh","mashbooh","halal","halal","halal",
            "halal","halal","halal","halal","halal","halal","mashbooh","halal","haram",
            "mashbooh","halal","halal","halal","halal","halal","halal","halal","halal",
            "halal","halal","halal","halal","halal","halal","halal","halal","halal",
            "halal","halal","halal","halal","halal","halal","halal","halal","halal",
            "halal","haram","halal","halal","halal","halal"
        ],
        "frequency_in_products": [
            5745,5268,4041,2120,1843,2099,2222,1286,1560,1193,633,578,24,0,
            81,0,0,73,908,166,7,4,0,214,
            0,0,320,38,163,403,255,28,649,1123,459,284,
            146,61,482,975,858,3,2,212,17,390,92,358,49,177
        ],
        "risk_level": [
            "low","low","low","medium","high","low","low","low",
            "low","low","low","low","low","low","high","low","high",
            "high","low","low","low","low","low","low","low","low",
            "low","low","low","low","low","low","low","low","low",
            "low","low","low","low","low","low","low","low","low",
            "low","high","low","low","low","low"
        ],
    })

    df_cert = pd.DataFrame({
        "status": ["Development","New","NoCertificate","Renew"],
        "tanpa_bahan": [393, 26823, 15336, 1162],
        "dengan_bahan": [7, 7, 15703, 22],
    })
    df_cert["total"] = df_cert["tanpa_bahan"] + df_cert["dengan_bahan"]

    top_ingredients = ["salt","water","sugar","beef","spice","citric_acid","apple",
                       "flavouring","antioxidant","dextrose"]
    cooc_matrix = np.array([
        [5745,3655,2162,1535,1546,1007,322,959,522,1024],
        [3655,5268,1899,1356,1280,1084,623,887,409,780],
        [2162,1899,4041,666,783,964,762,559,639,447],
        [1535,1356,666,2120,763,252,9,696,178,524],
        [1546,1280,783,763,1843,352,111,368,189,454],
        [1007,1084,964,252,352,2099,346,226,358,196],
        [322,623,762,9,111,346,2222,63,433,78],
        [959,887,559,696,368,226,63,1286,153,400],
        [522,409,639,178,189,358,433,153,1560,206],
        [1024,780,447,524,454,196,78,400,206,1193]
    ])
    df_cooc = pd.DataFrame(cooc_matrix, index=top_ingredients, columns=top_ingredients)

    df_clusters = pd.DataFrame({
        "cluster_label": [
            "C1 Bumbu & Gurih",
            "C2 Cemilan & Sayur",
            "C3 Jus & Bayi",
            "C4 Tepung & Sereal",
            "C5 Selai & Pemanis",
            "C6 Daging Sapi",
            "C7 Komoditas Mentah",
            "C8 Permen & Susu"
        ],
        "n_products":    [4759, 4571, 1216, 403, 1538, 522, 1100, 1630],
        "avg_ingredients":[19.6, 4.2, 8.0, 24.8, 4.5, 3.4, 1.8, 14.6],
        "halal_pct":     [15.3, 83.3, 76.2, 2.7, 89.0, 6.9, 97.8, 38.2],
    })

    df_nutrition = pd.DataFrame({
        "nutrisi": ["Fat","Saturated Fat","Sodium","Fiber","Sugar","Protein"],
        "pct_non_zero": [0.002288, 0.001632, 0.002304, 0.001362, 0.002422, 0.001850],
    })

    # 2. Memanggil fungsi rendering dashboard storytelling [CRISP-DM: Deployment]
    output_dir = "output_halal"
    plot_data_storytelling_dashboard(df_ingredients, df_cert, df_cooc, df_clusters, df_nutrition, save_dir=output_dir)
    print("Pipeline data storytelling selesai dijalankan.")

if __name__ == "__main__":
    main()
