import pandas as pd
import numpy as np
import json
import os
import re

def find_file(filename):
    """
    Mencari lokasi berkas input di data/processed/ atau direktori induk.
    """
    candidates = [
        os.path.join("..", "data", "processed", filename),
        os.path.join("data", "processed", filename),
        filename,
        os.path.join("..", filename),
        os.path.join("..", "..", "data", "processed", filename),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"Berkas '{filename}' tidak ditemukan di jalur standar mana pun.")

def main():
    print("=== PIPELINE GENERATOR DATABASE COMPACT WEB DASHBOARD [CRISP-DM: Deployment] ===")
    
    try:
        clusters_csv = find_file("product_spectral_clusters.csv")
        status_csv = find_file("ingredients_halal_status.csv")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Silakan jalankan pipeline pemodelan terlebih dahulu.")
        return
        
    print(f"Memuat koordinat klaster dari: {clusters_csv}")
    print(f"Memuat kamus status kehalalan dari: {status_csv}")
    
    df_clusters = pd.read_csv(clusters_csv)
    df_status = pd.read_csv(status_csv)
    
    # Menyesuaikan indeks klaster ke 1-indexed (1 s.d 8) untuk antarmuka web
    # Jika data sudah 1-indexed, kita tidak menambahnya lagi.
    if df_clusters['cluster'].min() == 0:
        df_clusters['cluster'] = df_clusters['cluster'] + 1
        
    # Membangun kamus aturan status kehalalan bahan baku [CRISP-DM: Data Preparation]
    status_rules = {}
    for _, row in df_status.iterrows():
        name = str(row['name']).strip().lower()
        status = str(row['status']).strip()
        status_rules[name] = status
        
    inherent_halal = [
        'water', 'salt', 'apple', 'garlic', 'onion', 'corn',
        'sunflower oil', 'egg', 'sea salt', 'starch', 'carrot',
        'wheat', 'pepper', 'soybean', 'basil'
    ]
    for item in inherent_halal:
        status_rules[item] = 'Halal'
        
    status_rules['pork'] = 'Haraam'
    status_rules['lard'] = 'Haraam'
    status_rules['bacon'] = 'Haraam'
    status_rules['ham'] = 'Haraam'
    status_rules['gelatin'] = 'Mushbooh'
    status_rules['beef'] = 'Mushbooh'
    status_rules['cream'] = 'Mushbooh'
    status_rules['spice'] = 'Mushbooh'

    # Mengklasifikasikan produk secara objektif (Worst-case) [CRISP-DM: Data Preparation]
    def classify_product(ing_str):
        if pd.isna(ing_str) or not str(ing_str).strip():
            return 'Unknown'
        ings = [i.strip().lower() for i in str(ing_str).split(',') if i.strip()]
        has_mushbooh = False
        for clean in ings:
            if any(h in clean for h in ['pork', 'pig', 'lard', 'bacon', 'ham', 'e120', 'carmine', 'cochineal', 'karmin']):
                return 'Haraam'
            if any(m in clean for m in ['beef', 'meat', 'chicken', 'poultry', 'animal', 'gelatin', 'cheese', 'rennet']) or re.search(r'\bwhey\b', clean):
                has_mushbooh = True
            elif any(f in clean for f in ['flavour', 'flavor', 'perisa', 'vanilla essence']) or clean == 'vanilla extract':
                has_mushbooh = True
            elif any(e in clean for e in ['emulsifier', 'pengemulsi', 'e471', 'mono and diglycerides', 'lecithin', 'lesitin']):
                has_mushbooh = True
            else:
                ing_normalized = clean.replace('_', ' ')
                status = status_rules.get(clean) or status_rules.get(ing_normalized)
                if status is None:
                    for key, val in status_rules.items():
                        key_normalized = key.replace('_', ' ')
                        if key_normalized in ing_normalized or ing_normalized in key_normalized:
                            status = val
                            break
                if status == 'Haraam':
                    return 'Haraam'
                elif status == 'Mushbooh':
                    has_mushbooh = True
        return 'Mushbooh' if has_mushbooh else 'Halal'

    df_clusters['obj_status'] = df_clusters['ingredients'].apply(classify_product)
    
    # Mengekstrak 500 bahan baku terpopuler untuk profil klaster [CRISP-DM: Data Preparation]
    all_ingredients = []
    for ing_str in df_clusters['ingredients'].fillna(''):
        ings = [i.strip().lower() for i in str(ing_str).split(',') if i.strip()]
        all_ingredients.extend(ings)
    ing_series = pd.Series(all_ingredients)
    freq_counts = ing_series.value_counts()
    top_ingredients = freq_counts[freq_counts >= 10].index.tolist()
    
    print("Mengekstrak profil bahan dominan di tiap klaster...")
    temp_dict = {}
    ing_cols = []
    for ing in top_ingredients[:500]:
        col_name = f"ing_{ing[:40].replace(' ', '_').replace('.', '').replace('/', '_')}"
        temp_dict[col_name] = df_clusters['ingredients'].apply(lambda x: 1 if ing in str(x).lower() else 0).astype('int8')
        ing_cols.append(col_name)
    df_temp = pd.DataFrame(temp_dict)
    
    cluster_labels = {
        1: "Bumbu Penyedap, Sup Instan, & Olahan Gurih Berdaging",
        2: "Makanan Ringan, Sayur Awetan, & Produk Biji-bijian",
        3: "Jus Buah Alami, Smoothies, & Makanan Bayi Organik",
        4: "Produk Olahan Tepung Terigu & Sereal Terfortifikasi",
        5: "Saus Buah (Applesauce), Awetan Buah, & Produk Pemanis Buah",
        6: "Daging Sapi Segar & Olahan Daging Sapi Murni",
        7: "Produk Komoditas Pertanian Mentah & Minuman Alami",
        8: "Produk Permen (Confectionery), Roti Manis, & Olahan Susu/Cokelat"
    }
    
    cluster_profiles = []
    n_clusters = 8
    for cluster_idx in range(1, n_clusters + 1):
        c_mask = df_clusters['cluster'] == cluster_idx
        c_df = df_clusters[c_mask]
        total_c = len(c_df)
        
        cert_dist = c_df['certificate_status'].value_counts(normalize=True).to_dict()
        cert_str = ", ".join([f"{k}: {v*100:.1f}%" for k, v in cert_dist.items()])
        
        obj_counts = c_df['obj_status'].value_counts()
        halal_pct = (obj_counts.get('Halal', 0) / total_c) * 100
        mushbooh_pct = (obj_counts.get('Mushbooh', 0) / total_c) * 100
        haraam_pct = (obj_counts.get('Haraam', 0) / total_c) * 100
        
        c_temp_df = df_temp[c_mask]
        ing_means = c_temp_df[ing_cols].mean().to_dict()
        sorted_ings = sorted(ing_means.items(), key=lambda x: x[1], reverse=True)[:5]
        top_ings = [{'name': k[4:].replace('_', ' ').title(), 'pct': float(v * 100)} for k, v in sorted_ings]
        
        sample_prods = c_df['label'].dropna().head(5).tolist()
        
        cluster_profiles.append({
            'id': cluster_idx,
            'name': cluster_labels[cluster_idx],
            'size': total_c,
            'cert_status': cert_str,
            'halal_pct': float(halal_pct),
            'mushbooh_pct': float(mushbooh_pct),
            'haraam_pct': float(haraam_pct),
            'top_ingredients': top_ings,
            'samples': sample_prods
        })
        
    # Memadatkan data produk agar ringan dimuat oleh browser [CRISP-DM: Deployment]
    products_packed = []
    for _, row in df_clusters.iterrows():
        products_packed.append({
            'id': str(row['product_id']),
            'l': str(row['label']),
            'm': str(row['manufacturer']),
            's': str(row['certificate_status']),
            'i': str(row['ingredients']) if not pd.isna(row['ingredients']) else '',
            'c': int(row['cluster']),
            'u1': float(row['umap_1']),
            'u2': float(row['umap_2']),
            'o': str(row['obj_status'])
        })
        
    web_db = {
        'status_rules': status_rules,
        'clusters': cluster_profiles,
        'products': products_packed
    }
    
    # Buat sub-folder data jika belum ada
    os.makedirs("data", exist_ok=True)
    
    # Ekspor ke JSON
    json_path = os.path.join("data", "products_data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(web_db, f, ensure_ascii=False, indent=2)
    print(f"Compact JSON database disimpan di: {json_path} ({os.path.getsize(json_path) / 1024:.1f} KB)")
    
    # Ekspor ke MessagePack (opsional, jika modul terinstall)
    try:
        import msgpack
        msgpack_path = os.path.join("data", "products_data.msgpack")
        with open(msgpack_path, 'wb') as f:
            msgpack.pack(web_db, f)
        print(f"MessagePack database disimpan di: {msgpack_path} ({os.path.getsize(msgpack_path) / 1024:.1f} KB)")
    except ImportError:
        print("Pustaka 'msgpack' tidak ditemukan. Lewati ekspor biner MessagePack (tidak masalah, web akan menggunakan JSON).")

if __name__ == "__main__":
    main()
