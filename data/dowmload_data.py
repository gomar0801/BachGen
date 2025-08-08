import tarfile
import os

def extract_archive(archive_path, extract_to="data/mxl"):
    """Extrait un fichier .tar.gz dans un dossier cible"""
    if not os.path.exists(archive_path):
        raise FileNotFoundError(f"❌ Archive introuvable : {archive_path}")
    
    os.makedirs(extract_to, exist_ok=True)

    print(f"📦 Extraction de {archive_path} vers {extract_to} ...")
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=extract_to)
    print(f"✅ Extraction terminée dans : {extract_to}")
