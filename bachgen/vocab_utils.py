# bachgen/vocab_utils.py
from __future__ import annotations
from typing import Dict, Iterable, List, Tuple, Set
from pathlib import Path
import json
from collections import Counter

# -------------------------
# Lecture des fichiers tokens
# -------------------------

def iter_token_lines(files: Iterable[Path]) -> Iterable[List[str]]:
    """
    Itère sur les lignes de fichiers .txt contenant des tokens séparés par des espaces.
    Rend une liste de tokens par ligne (sans lignes vides).
    """
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                yield line.split()


# -------------------------
# Construction / (dé)serialisation vocab
# -------------------------

def build_vocab(
    token_files: Iterable[Path],
    specials: List[str] = ("[PAD]", "[UNK]", "<BOS>", "<EOS>"),
    min_freq: int = 1,
) -> Tuple[Dict[str, int], Dict[int, str]]:
    """
    Construit un vocab {token->id} et {id->token}.
    - specials apparaissent en tête, dans l'ordre donné.
    - min_freq filtre les tokens trop rares (redirigés vers [UNK] à l'encodage).
    """
    counts = Counter()
    for toks in iter_token_lines(token_files):
        counts.update(toks)

    # Assure la présence d’[UNK]
    specials = list(specials)
    if "[UNK]" not in specials:
        specials.append("[UNK]")

    token2id: Dict[str, int] = {}
    id2token: Dict[int, str] = {}
    next_id = 0

    # Spéciaux d'abord
    for sp in specials:
        if sp not in token2id:
            token2id[sp] = next_id
            id2token[next_id] = sp
            next_id += 1

    # Tokens “normaux” triés par fréquence décroissante puis ordre lexicographique
    items = [(tok, freq) for tok, freq in counts.items() if freq >= min_freq and tok not in token2id]
    items.sort(key=lambda x: (-x[1], x[0]))

    for tok, _ in items:
        token2id[tok] = next_id
        id2token[next_id] = tok
        next_id += 1

    return token2id, id2token


def save_vocab(path: Path, token2id: Dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(token2id, f, ensure_ascii=False, indent=2)


def load_vocab(path: Path) -> Tuple[Dict[str, int], Dict[int, str]]:
    with open(path, "r", encoding="utf-8") as f:
        token2id = json.load(f)
    # token2id = {token(str): id(int)}
    id2token = {int(idx): tok for tok, idx in token2id.items()}
    return token2id, id2token


# -------------------------
# Encodage / décodage en mémoire
# -------------------------

def encode_tokens(
    tokens: List[str],
    token2id: Dict[str, int],
    add_bos: bool = False,
    add_eos: bool = False,
) -> List[int]:
    """
    Convertit liste de tokens -> liste d'ids. Les inconnus vont sur [UNK].
    """
    if "[UNK]" not in token2id:
        raise ValueError("Le vocab ne contient pas [UNK].")

    ids: List[int] = []
    if add_bos and "<BOS>" in token2id:
        ids.append(token2id["<BOS>"])

    unk_id = token2id["[UNK]"]
    for t in tokens:
        ids.append(token2id.get(t, unk_id))

    if add_eos and "<EOS>" in token2id:
        ids.append(token2id["<EOS>"])

    return ids


def decode_ids(
    ids: List[int],
    id2token: Dict[int, str],
    drop_specials: Set[str] | None = None,
) -> List[str]:
    """
    Convertit liste d'ids -> liste de tokens.
    drop_specials pour omettre ex: {"[PAD]", "<BOS>", "<EOS>"}.
    """
    out: List[str] = []
    drop_specials = drop_specials or set()
    for i in ids:
        tok = id2token.get(int(i), "[UNK]")
        if tok in drop_specials:
            continue
        out.append(tok)
    return out


# -------------------------
# Helpers fichiers / dossiers
# -------------------------

def encode_file_to_ids(
    in_path: Path,
    out_path: Path,
    token2id: Dict[str, int],
    add_bos: bool = False,
    add_eos: bool = False,
) -> None:
    """
    Lit un .txt (tokens espace), écrit un .ids.txt (ids espace), 1 ligne => 1 ligne.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(in_path, "r", encoding="utf-8") as fin, open(out_path, "w", encoding="utf-8") as fout:
        for line in fin:
            toks = line.strip().split()
            if not toks:
                fout.write("\n")
                continue
            ids = encode_tokens(toks, token2id, add_bos=add_bos, add_eos=add_eos)
            fout.write(" ".join(str(i) for i in ids) + "\n")


def encode_dir_to_ids(
    token_dir: Path,
    ids_dir: Path,
    token2id: Dict[str, int],
    add_bos: bool = True,
    add_eos: bool = True,
    pattern: str = "*.txt",
) -> None:
    """
    Encode tous les fichiers 'pattern' de token_dir -> ids_dir avec même stem et suffixe .ids.txt
    """
    ids_dir.mkdir(parents=True, exist_ok=True)
    for tf in sorted(token_dir.glob(pattern)):
        out = ids_dir / (tf.stem + ".ids.txt")
        encode_file_to_ids(tf, out, token2id, add_bos=add_bos, add_eos=add_eos)


def decode_ids_file(
    ids_path: Path,
    vocab_path: Path,
    join_tokens: bool = True,
) -> str | List[str]:
    """
    Décoder rapidement un fichier .ids.txt via un vocab sauvegardé.
    """
    token2id, id2token = load_vocab(vocab_path)
    with open(ids_path, "r", encoding="utf-8") as f:
        ids = [int(x) for x in f.read().strip().split() if x.strip()]
    toks = decode_ids(ids, id2token)
    return " ".join(toks) if join_tokens else toks
