import re
import os
import pandas as pd

def find_ttl_file(custom_path=None):
    """
    Mencari lokasi file lodhalalturtle.ttl secara robust di beberapa jalur standar.
    """
    if custom_path and os.path.exists(custom_path):
        return custom_path
        
    candidates = [
        os.path.join("data", "raw", "lodhalalturtle.ttl"),
        "lodhalalturtle.ttl",
        os.path.join("..", "lodhalalturtle.ttl"),
        os.path.join("..", "data", "raw", "lodhalalturtle.ttl"),
        os.path.join("..", "..", "lodhalalturtle.ttl")
    ]
    
    for path in candidates:
        if os.path.exists(path):
            return path
            
    raise FileNotFoundError(
        "File 'lodhalalturtle.ttl' tidak ditemukan di data/raw/, root, atau folder induk."
    )

def parse_rdf_turtle_to_dataframe(ttl_path: str) -> pd.DataFrame:
    """
    Mengurai file RDF Turtle (.ttl) menggunakan ekspresi reguler (regex)
    dan mengonversinya menjadi Pandas DataFrame tabular.
    """
    print(f"Membaca berkas TTL dari: {ttl_path}...")
    with open(ttl_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    print("Mengurai RDF triples semantik...")
    products = {}      # prod_id -> {label, manufacturer, fat, sat_fat, sodium, fiber, sugar, protein}
    prod_certs = {}    # prod_id -> cert_id
    certs = {}         # cert_id -> {status, org}
    prod_ingreds = {}  # prod_id -> list of ingredients

    # Pola ekspresi reguler untuk parsing
    type_pattern = re.compile(r'^halalf:(\S+)\s+a\s+foodlirmm:FoodProduct\s*;')
    label_pattern = re.compile(r'rdfs:label\s+"([^"]+)"')
    manufacturer_pattern = re.compile(r'gr:hasManufacturer\s+halalm:(\S+)')
    fat_pattern = re.compile(r'foodlirmm:fatPer100g\s+([\d\.]+)')
    sat_fat_pattern = re.compile(r'foodlirmm:saturatedFatPer100g\s+([\d\.]+)')
    sodium_pattern = re.compile(r'foodlirmm:sodiumPer100g\s+([\d\.]+)')
    fiber_pattern = re.compile(r'foodlirmm:fiberPer100g\s+([\d\.]+)')
    sugar_pattern = re.compile(r'foodlirmm:sugarsPer100g\s+([\d\.]+)')
    protein_pattern = re.compile(r'foodlirmm:proteinsPer100g\s+([\d\.]+)')

    cert_type_pattern = re.compile(r'^halalc:(\S+)\s+a\s+halalv:HalalCertificate\s*;')
    cert_status_pattern = re.compile(r'halalv:halalStatus\s+"([^"]+)"')
    cert_org_pattern = re.compile(r'halalv:OrgCert\s+halals:(\S+)')

    current_prod = None
    current_cert = None

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        prod_match = type_pattern.match(line_str)
        if prod_match:
            current_prod = prod_match.group(1)
            current_cert = None
            products[current_prod] = {
                'fat': 0.0, 'saturatedFat': 0.0, 'sodium': 0.0,
                'fiber': 0.0, 'sugar': 0.0, 'protein': 0.0,
                'manufacturer': 'Unknown', 'label': ''
            }
            continue
            
        cert_match = cert_type_pattern.match(line_str)
        if cert_match:
            current_cert = cert_match.group(1)
            current_prod = None
            certs[current_cert] = {'status': 'Unknown', 'org': 'Unknown'}
            continue
            
        if current_prod:
            fat_m = fat_pattern.search(line_str)
            if fat_m: products[current_prod]['fat'] = float(fat_m.group(1))
            
            sat_fat_m = sat_fat_pattern.search(line_str)
            if sat_fat_m: products[current_prod]['saturatedFat'] = float(sat_fat_m.group(1))
            
            sodium_m = sodium_pattern.search(line_str)
            if sodium_m: products[current_prod]['sodium'] = float(sodium_m.group(1))
            
            fiber_m = fiber_pattern.search(line_str)
            if fiber_m: products[current_prod]['fiber'] = float(fiber_m.group(1))
            
            sugar_m = sugar_pattern.search(line_str)
            if sugar_m: products[current_prod]['sugar'] = float(sugar_m.group(1))
            
            protein_m = protein_pattern.search(line_str)
            if protein_m: products[current_prod]['protein'] = float(protein_m.group(1))
            
            label_m = label_pattern.search(line_str)
            if label_m: products[current_prod]['label'] = label_m.group(1)
            
            man_m = manufacturer_pattern.search(line_str)
            if man_m: products[current_prod]['manufacturer'] = man_m.group(1)
            
            if line_str.endswith('.'):
                current_prod = None
                
        elif current_cert:
            status_m = cert_status_pattern.search(line_str)
            if status_m: certs[current_cert]['status'] = status_m.group(1)
            
            org_m = cert_org_pattern.search(line_str)
            if org_m: certs[current_cert]['org'] = org_m.group(1)
            
            if line_str.endswith('.'):
                current_cert = None
                
        else:
            if "foodlirmm:certificate" in line_str:
                parts = line_str.split("foodlirmm:certificate")
                if len(parts) == 2:
                    p_id = parts[0].strip().replace("halalf:", "")
                    c_id = parts[1].strip().replace("halalc:", "").replace(".", "").strip()
                    prod_certs[p_id] = c_id
                    
            elif "food:containsIngredient" in line_str:
                parts = line_str.split("food:containsIngredient")
                if len(parts) == 2:
                    p_id = parts[0].strip().replace("halalf:", "")
                    ing_list = parts[1].strip().replace("halali:", "").replace(".", "").split(",")
                    prod_ingreds[p_id] = [ing.strip() for ing in ing_list if ing.strip()]

    print(f"Berhasil mengurai {len(products)} produk pangan.")
    
    # Membangun daftar baris
    data_list = []
    for p_id, p_info in products.items():
        cert_id = prod_certs.get(p_id)
        c_status = 'NoCertificate'
        c_org = 'None'
        if cert_id and cert_id in certs:
            c_status = certs[cert_id]['status']
            c_org = certs[cert_id]['org']
            
        ingreds_list = prod_ingreds.get(p_id, [])
        ingreds_str = ",".join(ingreds_list)
        
        row = {
            'product_id': p_id,
            'label': p_info['label'],
            'manufacturer': p_info['manufacturer'],
            'fat': p_info['fat'],
            'saturated_fat': p_info['saturatedFat'],
            'sodium': p_info['sodium'],
            'fiber': p_info['fiber'],
            'sugar': p_info['sugar'],
            'protein': p_info['protein'],
            'certificate_id': cert_id if cert_id else '',
            'certificate_status': c_status,
            'certificate_org': c_org,
            'ingredients': ingreds_str
        }
        data_list.append(row)

    return pd.DataFrame(data_list)
