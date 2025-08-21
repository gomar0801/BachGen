# bachgen/batch_convert_mxl_to_musicxml.py
import os
import warnings
from pathlib import Path
from typing import Iterable, List, Tuple, Union, Optional

import pandas as pd
from tqdm import tqdm
import concurrent.futures

from music21 import musicxml
warnings.simplefilter("ignore", musicxml.xmlToM21.MusicXMLWarning)

from bachgen.mxl_to_musicxml import convert_mxl_to_musicxml  # fonction unitaire

def _clean_input_to_series(
    items: Union[pd.DataFrame, Iterable[str]],
    path_col: str = "mxl"
) -> pd.Series:
    """
    Normalise l'entrée (DataFrame ou liste de chemins str) en une Series de chemins relatifs .mxl
    """
    if isinstance(items, pd.DataFrame):
        if path_col not in items.columns:
            raise ValueError(f"Colonne '{path_col}' introuvable dans le DataFrame.")
        s = items[path_col]
    else:
        s = pd.Series(list(items), name=path_col)

    s = s.dropna().astype(str)
    s = s[s.str.lower().str.endswith(".mxl")]
    s = s.drop_duplicates()
    return s


def convert_many_mxl_to_musicxml(
    items: Union[pd.DataFrame, Iterable[str]],
    mxl_root: Union[str, Path],
    out_dir: Union[str, Path],
    path_col: str = "mxl",
    timeout: int = 10,
    max_workers: int = 1,
    resume: bool = True,
    error_log_csv: Optional[Union[str, Path]] = None,
) -> Tuple[int, List[Tuple[str, str]]]:
    """
    Convertit en série des fichiers .mxl vers .musicxml.

    Args:
        items: DataFrame avec la colonne `path_col` OU iterable de chemins relatifs .mxl
        mxl_root: dossier racine où se trouvent les .mxl (ex: 'data/mxl')
        out_dir: dossier de sortie (ex: 'data/musicxml_classical_piano_convert')
        path_col: nom de la colonne qui contient les chemins (si DataFrame)
        timeout: secondes max par fichier (sinon -> TimeoutError)
        max_workers: nb workers pour l’executor (laisser 1 si instable)
        resume: si True, on saute les sorties déjà existantes
        error_log_csv: si fourni, on écrit un CSV des erreurs (cols: input, error)

    Returns:
        (done_count, errors) où errors = liste de tuples (input_path, message)
    """
    mxl_root = Path(mxl_root)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rel_paths = _clean_input_to_series(items, path_col=path_col)
    total = len(rel_paths)

    def _job(in_path: Path, out_path: Path):
        convert_mxl_to_musicxml(str(in_path), str(out_path))

    errors: List[Tuple[str, str]] = []
    done = 0

    # Important: avec music21, rester conservateur => ThreadPool + max_workers petit
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {}
        for rel in rel_paths:
            in_path = mxl_root / rel
            if not in_path.exists():
                errors.append((str(in_path), "missing"))
                continue

            out_name = in_path.stem + ".musicxml"
            out_path = out_dir / out_name

            if resume and out_path.exists():
                # déjà converti
                continue

            futures[ex.submit(_job, in_path, out_path)] = (in_path, out_path)

        for fut in tqdm(concurrent.futures.as_completed(futures, timeout=None),
                        total=len(futures), desc="Converting"):
            in_path, out_path = futures[fut]
            try:
                fut.result(timeout=timeout)
                done += 1
            except concurrent.futures.TimeoutError:
                errors.append((str(in_path), f"timeout>{timeout}s"))
                # Nettoyage éventuel d’un fichier incomplet
                try:
                    if out_path.exists():
                        out_path.unlink()
                except Exception:
                    pass
            except Exception as e:
                errors.append((str(in_path), str(e)))
                try:
                    if out_path.exists():
                        out_path.unlink()
                except Exception:
                    pass

    if error_log_csv:
        pd.DataFrame(errors, columns=["input", "error"]).to_csv(error_log_csv, index=False)

    print(f"✅ Conversion terminée: {done} fichiers créés dans {out_dir}")
    if errors:
        print(f"⚠️ {len(errors)} problème(s). Exemples:")
        for e in errors[:10]:
            print("  -", e)

    return done, errors
