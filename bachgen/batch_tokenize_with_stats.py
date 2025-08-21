# bachgen/tokenize_batch.py
from __future__ import annotations
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout
import csv
from typing import Dict, List, Tuple, Iterable, Optional

from bachgen.score_to_tokens_simplify import MusicXML_to_tokens


# --- remplace TOUTE la fonction par ceci ---
def _parse_debug_log(log_lines):
    """
    Parse les logs de debug et renvoie un dict de stats, avec les % calculés
    sur total_items_seen.
    """
    total_notes_seen      = 0
    rests_kept            = 0
    rests_ignored_overlap = 0
    transparent_ignored   = 0
    harmonize_events      = 0

    for line in log_lines:
        if "[note_to_tokens] Traitement d'une note ou d'un groupe" in line or "CHORD_detecté" in line:
            total_notes_seen += 1
        elif "Note transparente détectée, ignorée" in line:
            transparent_ignored += 1
        elif "→ Rest detected" in line:
            rests_kept += 1
        elif "Silences superposés détectés, ils sont ignorés" in line:
            rests_ignored_overlap += 1
        elif "Durée harmonisée de l'accord" in line:
            harmonize_events += 1

    # Dénominateur commun
    denom = total_notes_seen if total_notes_seen else 1

    transparent_pct       = round(transparent_ignored   / denom * 100.0, 3) if total_notes_seen else 0.0
    overlap_rest_pct      = round(rests_ignored_overlap / denom * 100.0, 3) if total_notes_seen else 0.0
    harmonize_events_pct  = round(harmonize_events      / denom * 100.0, 3) if total_notes_seen else 0.0

    return {
        "total_items_seen": total_notes_seen,
        "transparent_ignored": transparent_ignored,
        "rests_kept": rests_kept,
        "rests_ignored_overlap": rests_ignored_overlap,
        "harmonize_events": harmonize_events,
        "transparent_pct": transparent_pct,
        "overlap_rest_pct": overlap_rest_pct,
        "harmonize_events_pct": harmonize_events_pct,
    }



def tokenize_with_stats(xml_path: Path, note_name: bool = True) -> Tuple[List[str], Dict[str, int | float]]:
    """
    Lance MusicXML_to_tokens en capturant les prints de debug,
    calcule les mêmes stats que dans ton notebook.
    """
    buf = StringIO()
    with redirect_stdout(buf):
        tokens = MusicXML_to_tokens(str(xml_path), note_name=note_name)
    log_lines = buf.getvalue().splitlines()

    stats = _parse_debug_log(log_lines)
    stats["file"] = xml_path.name
    return tokens, stats


def tokenize_folder_with_stats(
    src_dir: Path | str,
    out_tok_dir: Path | str,
    stats_csv: Path | str,
    note_name: bool = True,
    pattern: str = "*.musicxml",
    resume: bool = True,
    verbose: bool = True,
) -> List[Dict[str, int | float]]:
    """
    Tokenise tous les fichiers .musicxml d'un dossier, écrit 1 .txt par fichier et un CSV de stats.

    Args:
        src_dir: dossier source contenant les .musicxml
        out_tok_dir: dossier de sortie pour les .txt de tokens
        stats_csv: chemin du CSV récapitulatif
        note_name: passe tel quel à MusicXML_to_tokens (True = noms de notes; False = midi ids)
        pattern: motif de recherche (par défaut "*.musicxml")
        resume: si True, ne retokenise pas les fichiers déjà présents
        verbose: prints “✅/❌” comme dans le notebook

    Returns:
        La liste des dicts de stats.
    """
    src_dir = Path(src_dir)
    out_tok_dir = Path(out_tok_dir)
    out_tok_dir.mkdir(parents=True, exist_ok=True)
    stats_path = Path(stats_csv)
    stats_path.parent.mkdir(parents=True, exist_ok=True)

    all_stats: List[Dict[str, int | float]] = []

    for xml_file in sorted(src_dir.rglob(pattern)):
        out_txt = out_tok_dir / (xml_file.stem + ".txt")
        if resume and out_txt.exists():
            if verbose:
                print(f"⏭️  {xml_file.relative_to(src_dir)} (déjà présent)")
            continue

        try:
            tokens, stats = tokenize_with_stats(xml_file, note_name=note_name)
            out_txt.write_text(" ".join(tokens), encoding="utf-8")
            all_stats.append(stats)
            if verbose:
                print(
                    f"✅ {xml_file.relative_to(src_dir)}  "
                    f"[transp {stats['transparent_pct']}% | "
                    f"overl.rest {stats['overlap_rest_pct']}% | "
                    f"harmo {stats['harmonize_events_pct']}% (count={stats['harmonize_events']})]"
                )
        except Exception as e:
            if verbose:
                print(f"❌ {xml_file} -> {e}")

    # CSV
    with stats_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "file", "total_items_seen", "transparent_ignored",
                "rests_kept", "rests_ignored_overlap", "harmonize_events",
                "transparent_pct", "overlap_rest_pct","harmonize_events_pct",
            ],
        )
        writer.writeheader()
        writer.writerows(all_stats)

    if verbose:
        print(f"\n📊 Stats écrites dans: {stats_path}")
        print(f"🧾 Tokens enregistrés dans: {out_tok_dir}")

    return all_stats
