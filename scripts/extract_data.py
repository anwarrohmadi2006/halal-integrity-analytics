import os
import sys

# Tambahkan folder root final_project ke sys.path untuk impor modular
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parser import find_ttl_file, parse_rdf_turtle_to_dataframe

def main():
    print("=== PIPELINE EKSTRAKSI DATA SEMANTIK ===")
    
    # 1. Mencari lokasi file data mentah (TTL) [CRISP-DM: Data Understanding]
    try:
        ttl_path = find_ttl_file()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
        
    # 2. Mengurai struktur RDF Turtle menjadi DataFrame [CRISP-DM: Data Preparation]
    df = parse_rdf_turtle_to_dataframe(ttl_path)
    
    # 3. Menyimpan hasil ekstraksi tabular ke direktori data/processed/
    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    os.makedirs(os.path.join("..", "data", "processed"), exist_ok=True) # Jaga-jaga jika dieksekusi dari subfolder
    
    output_path = os.path.join("data", "processed", "halal_products_tabular.csv")
    df.to_csv(output_path, index=False)
    print(f"Data tabular berhasil disimpan ke: {output_path}")
    
    # Tampilkan statistik sederhana
    print("\nDistribusi Status Sertifikat:")
    print(df['certificate_status'].value_counts())

if __name__ == "__main__":
    main()
