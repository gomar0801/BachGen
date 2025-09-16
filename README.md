# 🎼 BachGen — MusicXML → Tokens → GPT-2 → MusicXML

Un pipeline complet pour :
1. **Convertir** des fichiers `.mxl` en `.musicxml`  
2. **Tokeniser** les partitions (MusicXML → séquence de tokens textuels robustes)  
3. **Construire** un vocabulaire et encoder en IDs  
4. **Entraîner** un modèle **GPT-2** causal sur ces séquences  
5. **Générer** de nouvelles partitions musicales et les **reconstruire** en MusicXML  

Projet réalisé au **SCAI (Sorbonne Center for Artificial Intelligence)**, été 2025.

---

## 🚀 Installation rapide (Google Colab / local)

Dans un notebook :

```bash
!rm -rf BachGen && git clone https://github.com/gomar0801/BachGen.git
!chmod +x ./BachGen/scripts/setup.sh
!./BachGen/scripts/setup.sh
```

Puis :

```python
from bachgen.display_and_play_partition import display_and_play
display_and_play('./BachGen/musicxml_sample/minimal.musicxml')
```

---

## 📂 Structure du dépôt

```
BachGen/
├── bachgen/                  # code source du pipeline
│   ├── score_to_tokens_simplify.py   # MusicXML → tokens
│   ├── tokens_to_score.py            # tokens → MusicXML
│   ├── convert_mxl.py                # conversion .mxl → .musicxml
│   ├── batch_tokenize.py             # tokenisation par lot + stats
│   ├── vocab_utils.py                # vocabulaire, encode/decode
│   ├── training.py                   # dataset + entraînement GPT-2
│   ├── generation.py                 # génération de partitions
│   └── display_and_play_partition.py # affichage/écoute (music21)
├── scripts/
│   ├── setup.sh                      # installation des dépendances
│   ├── download_data.py              # données Zenodo
│   └── extract_archives.py           # extraction .tar.gz/.zip
├── tests/                            # tests unitaires
│   ├── test_xml_to_tokens.py
│   ├── test_tokens_to_xml.py
│   ├── test_roundtrip.py
│   └── conftest.py
├── musicxml_sample/                  # exemples MusicXML
├── token_sample/                     # exemples tokens
├── notebooks/                        # notebooks Colab
│   └── BachGen_Pipeline.ipynb
├── requirements.txt
└── README.md
```

---

## 🧪 Tests

Lancer tous les tests :

```bash
pytest
```

Test d’un fichier spécifique :

```bash
pytest tests/test_xml_to_tokens.py -v
```

---

## 🎼 Exemple de format de tokens

Exemple minimal :

```
R bar clef_treble key_natural_0 time_4/4 note_C4 len_4 L bar
```

Où :
- `R` = main droite (portée aiguë)  
- `L` = main gauche (portée grave)  
- `bar` = séparation de mesure  
- `clef_treble` = clé de sol  
- `key_natural_0` = do majeur (aucun dièse/bémol)  
- `time_4/4` = signature rythmique 4/4  
- `note_C4` = note Do à l'octave 4  
- `len_4` = durée de 4 temps  

---

## 📊 Tokenisation robuste + statistiques

La tokenisation gère plusieurs cas problématiques détectés dans ScoreTransformers :
- **Notes transparentes** (`print-object="no"`) → ignorées  
- **Silences superposés à des notes** → ignorés  
- **Multi-voix / accords** → réécriture des mesures en 1 voix avec harmonisation des durées  
- **Absence de voice** → ajout implicite pour consistance  

Chaque partition est analysée et un CSV est produit avec :
- `% notes transparentes ignorées`  
- `% silences superposés ignorés`  
- `% positions harmonisées, notes jouées en meme temps mais d'une durée differente harmonisées en 1 accord d'une meme durée`

Exemple de résultats (corpus classique piano) :
- **Notes transparentes ignorées** : ~1.3 % en moyenne  
- **Silences superposés ignorés** : ~4 %  en moyenne
- **Harmonisations appliquées** : ~20 % des éléments (bémol du projet)  

---

## 🤖 Entraînement GPT-2

- Dataset : partitions piano classiques (MusicXML → tokens → IDs)  
- Vocabulaire : ~364 tokens  
- Contexte : 1024 tokens  
- Modèle : GPT-2 (4 couches, 4 têtes, 1024 dim.)  
- Résultats :
  - **Validation loss** : ~0.88  
  - **Test perplexity** : ~2.4  

---

## 🎹 Génération

Exemple : génération depuis BOS uniquement (fin à EOS) :

```python
from bachgen.generation import generate_piece, ids_to_tokens, tokens_to_musicxml_file

piece_ids = generate_piece(
    model_dir="./final_model_gpt2_ids",
    vocab_path="data/vocab/token2id.json",
    primer_tokens=None,
    max_new_tokens=300,
    top_k=8
)

tokens = ids_to_tokens(piece_ids, "data/vocab/token2id.json", drop_specials={"[PAD]","<BOS>","<EOS>"})
tokens_to_musicxml_file(tokens, "outputs/generated.musicxml")
```

Exemple avec un **prompt** :

```python
primer = ["R", "bar", "key_flat_3", "time_4/4", "clef_treble"]
piece_ids = generate_piece(
    model_dir="./final_model_gpt2_ids",
    vocab_path="data/vocab/token2id.json",
    primer_tokens=primer,
    max_new_tokens=300,
    top_k=8
)
```

---

## 📓 Notebook Colab

👉 [Ouvrir le notebook sur Colab](VOTRE-LIEN-COLAB-ICI)  

Ce notebook montre le pipeline complet : download → conversion → tokenisation → vocab/IDs → entraînement → génération.

---

## 🙏 Remerciements

- **SCAI – Sorbonne Center for Artificial Intelligence**  
- **Corpus PDMX (Zenodo)**  
- Les communautés *music21* et *Hugging Face*
