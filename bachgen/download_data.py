# bachgen/download_data.py

import os
import requests

def download_file(url, output_path):
    """Télécharge un fichier depuis une URL vers un chemin local."""
    if os.path.exists(output_path):
        print(f"✅ Le fichier existe déjà : {output_path}")
        return
    print(f"⬇️  Téléchargement depuis {url} ...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Fichier téléchargé : {output_path}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    mxl_url = "https://zenodo.org/records/15571083/files/mxl.tar.gz?download=1"
    download_file(mxl_url, "data/mxl.tar.gz")
