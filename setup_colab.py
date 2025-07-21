import os
import sys
import subprocess
from music21 import environment

def setup_colab(repo_url, requirements_url=None):
    """
    Configure l'environnement Google Colab pour l'utilisation du projet BachGen.

    - Installe MuseScore pour afficher les partitions
    - Configure music21 pour utiliser MuseScore
    - Clone le dépôt GitHub
    - Installe les dépendances à partir d'un fichier requirements.txt (optionnel)

    Args:
        repo_url (str): URL HTTPS du dépôt GitHub (ex: https://github.com/gomar0801/BachGen.git)
        requirements_url (str, optional): URL brute vers le requirements.txt

    code dans colab :
        from setup_colab import setup_colab

        setup_colab(
            "https://github.com/gomar0801/BachGen.git",
            "https://raw.githubusercontent.com/gomar0801/BachGen/main/requirements.txt"
        )
    """
    print("📦 Installation de MuseScore...")
    subprocess.run(['apt-get', 'install', '-y', 'musescore'], check=True)                                   

    print("🎼 Configuration de music21...")
    us = environment.UserSettings()
    us['musescoreDirectPNGPath'] = '/usr/bin/mscore'  # ou '/usr/bin/musescore' selon les versions

    print("📁 Clonage du dépôt GitHub...")
    os.system(f'git clone {repo_url}')
    repo_name = repo_url.rstrip('.git').split('/')[-1]
    sys.path.append(f'/content/{repo_name}')

    if requirements_url:
        print("📚 Installation des dépendances...")
        os.system(f'pip install -r {requirements_url}')

    print("✅ Environnement prêt !")

# Exemple d'utilisation :
# setup_colab("https://github.com/gomar0801/BachGen.git", "https://raw.githubusercontent.com/gomar0801/BachGen/main/requirements.txt")
