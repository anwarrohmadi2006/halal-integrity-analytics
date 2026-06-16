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
            "halal","halal","halal","halal","halal","halal","halal","mashbooh","halal",
            "halal","halal","halal","halal","halal","mashbooh","haram","haram","mashbooh",
            "halal","halal","halal","halal","mashbooh","mashbooh","mashbooh","mashbooh",
            "halal","halal","halal","halal","halal","halal","halal","halal","halal","halal",
            "halal","halal","halal","halal","halal","halal","halal","halal","halal",
            "haram","haram","halal","halal","halal"
        ],
        "frequency_in_products": [
            5745,5268,4041,2120,1843,2099,2222,1286,1560,1193,980,1450,2340,870,
            620,180,95,760,1120,890,1340,1080,950,680,540,490,430,380,560,320,
            740,1680,1240,2560,1890,780,650,480,920,1640,1380,1290,1950,1120,
            480,42,38,890,760,1240
        ],
        "risk_level": [
            "low","low","low","medium","low","low","low","high","low","low","low","low",
            "medium","medium","high","high","high","high","low","low","low","low","high",
            "high","high","high","low","low","low","low","low","low","low","low","low",
            "low","low","low","low","low","low","low","low","low","low","high","high",
            "low","low","low"
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
        [1024,780,447,524,454,196,78,400,206,1193],
    ])
    df_cooc = pd.DataFrame(cooc_matrix, index=top_ingredients, columns=top_ingredients)

    df_clusters = pd.DataFrame({
        "cluster_label": ["C1 Sederhana","C2 Kompleks","C3 Berdaging","C4 Manis",
                          "C5 Asam","C6 Olahan","C7 Mentah","C8 Premium"],
        "n_products":    [2847,1983,1567,2234,1124,1876,1543,565],
        "avg_ingredients":[3.2,8.7,6.1,7.4,5.8,9.2,2.4,11.3],
        "halal_pct":     [98.1,87.3,91.2,94.7,96.8,85.9,99.4,82.6],
    })

    df_nutrition = pd.DataFrame({
        "nutrisi": ["Fat","Saturated Fat","Sodium","Fiber","Sugar","Protein"],
        "pct_non_zero": [0.2288,0.1632,0.2304,0.1362,0.2422,0.1850],
    })

    # 2. Memanggil fungsi rendering dashboard storytelling [CRISP-DM: Deployment]
    output_dir = "output_halal"
    plot_data_storytelling_dashboard(df_ingredients, df_cert, df_cooc, df_clusters, df_nutrition, save_dir=output_dir)
    print("Pipeline data storytelling selesai dijalankan.")

if __name__ == "__main__":
    main()
