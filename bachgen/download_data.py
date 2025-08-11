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

def download_all():
    """Télécharge tous les fichiers nécessaires dans le dossier data/"""
    os.makedirs("data", exist_ok=True)

    files = {
        "mxl.tar.gz": "https://zenodo.org/records/15571083/files/mxl.tar.gz?download=1",
        "PDMX.csv": "https://zenodo.org/records/15571083/files/PDMX.csv?download=1"
    }

    for filename, url in files.items():
        path = os.path.join("data", filename)
        download_file(url, path)

if __name__ == "__main__":
    download_all()