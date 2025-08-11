import pandas as pd
import os

def load_and_filter_piano_classical(csv_path="data/PDMX.csv"):
    """
    Charge PDMX.csv et filtre les partitions de piano (2 pistes) et de genre 'classical'.
    
    Args:
        csv_path (str): Chemin vers le fichier PDMX.csv
    
    Returns:
        pd.DataFrame: DataFrame filtré
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"❌ Fichier introuvable : {csv_path}")
    
    # Lecture du CSV
    df = pd.read_csv(csv_path)
    
    # Filtrage
    df_piano = df[df['n_tracks'] == 2]
    df_piano_classical = df_piano[df_piano['genres'] == 'classical']
    
    print(f"🎹 {len(df_piano_classical)} partitions de piano (genre classique) trouvées.")
    return df_piano_classical
