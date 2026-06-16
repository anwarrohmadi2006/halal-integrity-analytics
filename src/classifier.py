import re
import os
import pandas as pd

def load_halal_status_dict(status_csv_path=None):
    """
    Memuat kamus status kehalalan bahan baku dari file ingredients_halal_status.csv.
    """
    status_dict = {}
    
    # Jalur kandidat standar
    candidates = [
        status_csv_path,
        os.path.join("data", "processed", "ingredients_halal_status.csv"),
        "ingredients_halal_status.csv",
        os.path.join("..", "ingredients_halal_status.csv"),
        os.path.join("..", "data", "processed", "ingredients_halal_status.csv")
    ]
    
    found_path = None
    for path in candidates:
        if path and os.path.exists(path):
            found_path = path
            break
            
    if found_path:
        df_status = pd.read_csv(found_path)
        for _, row in df_status.iterrows():
            status_dict[str(row['name']).strip().lower()] = str(row['status']).strip()
            
    # Penyesuaian aturan bawaan (Inherent Halal & Haram spesifik)
    # - Hapus 'cream' dan 'spice' dari inherent_halal karena bisa berupa carrier lemak babi/hewan
    inherent_halal = [
        'water', 'salt', 'apple', 'garlic', 'onion', 'corn',
        'sunflower oil', 'egg', 'sea salt', 'starch', 'carrot',
        'wheat', 'pepper', 'soybean', 'basil'
    ]
    for item in inherent_halal:
        status_dict[item] = 'Halal'
        
    status_dict['pork'] = 'Haraam'
    status_dict['lard'] = 'Haraam'
    status_dict['bacon'] = 'Haraam'
    status_dict['ham'] = 'Haraam'
    status_dict['gelatin'] = 'Mushbooh'
    status_dict['beef'] = 'Mushbooh'
    status_dict['cream'] = 'Mushbooh'
    status_dict['spice'] = 'Mushbooh'
    
    return status_dict

def classify_product(ing_str, status_dict):
    """
    Mengklasifikasikan kehalalan objektif suatu produk berdasarkan daftar bahan bakunya.
    Menggunakan substring containment matching untuk menghindari kegagalan token.
    """
    if pd.isna(ing_str) or not str(ing_str).strip():
        return 'Unknown'
        
    ings = [i.strip().lower() for i in str(ing_str).split(',') if i.strip()]
    has_mushbooh = False
    
    for clean in ings:
        # 1. Aturan Haram Mutlak
        if any(h in clean for h in ['pork', 'pig', 'lard', 'bacon', 'ham', 'e120', 'carmine', 'cochineal', 'karmin']):
            return 'Haraam'
            
        # 2. Aturan Syubhat (Mushbooh) Hewani
        if any(m in clean for m in ['beef', 'meat', 'chicken', 'poultry', 'animal', 'gelatin', 'cheese', 'rennet']) or re.search(r'\bwhey\b', clean):
            has_mushbooh = True
            continue
            
        # 3. Aturan Syubhat Perisa
        if any(f in clean for f in ['flavour', 'flavor', 'perisa', 'vanilla essence']) or clean == 'vanilla extract':
            has_mushbooh = True
            continue
            
        # 4. Aturan Syubhat Emulsifier/Penstabil
        if any(e in clean for e in ['emulsifier', 'pengemulsi', 'e471', 'mono and diglycerides', 'lecithin', 'lesitin']):
            has_mushbooh = True
            continue
            
        # Fallback pencarian kamus
        ing_normalized = clean.replace('_', ' ')
        status = status_dict.get(clean) or status_dict.get(ing_normalized)
        if status is None:
            for key, val in status_dict.items():
                key_normalized = key.replace('_', ' ')
                if key_normalized in ing_normalized or ing_normalized in key_normalized:
                    status = val
                    break
        if status == 'Haraam':
            return 'Haraam'
        elif status == 'Mushbooh':
            has_mushbooh = True
            
    return 'Mushbooh' if has_mushbooh else 'Halal'
