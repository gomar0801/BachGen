# bachgen/training/splits.py
from __future__ import annotations
from typing import List, Tuple
from pathlib import Path
import json
import random

def load_vocab_ids(vocab_path: Path):
    """
    Charge le vocab {token->id} et renvoie (VOCAB_SIZE, PAD, BOS, EOS).
    On tolère plusieurs variantes de noms.
    """
    vocab = json.loads(Path(vocab_path).read_text(encoding="utf-8"))
    vocab_size = len(vocab)

    def _get_id(*cands, default):
        for c in cands:
            if c in vocab:
                return vocab[c]
        return default

    pad_id = _get_id("<PAD>", "[PAD]", "PAD", default=0)
    bos_id = _get_id("<BOS>", "<bos>", "BOS", default=1)
    eos_id = _get_id("<EOS>", "<eos>", "EOS", default=2)
    return vocab_size, pad_id, bos_id, eos_id

def read_ids_file(path: Path) -> List[int]:
    txt = Path(path).read_text(encoding="utf-8").strip()
    return [] if not txt else [int(x) for x in txt.split()]

def load_all_ids(ids_dir: Path, suffix: str = ".txt") -> List[List[int]]:
    """
    Charge toutes les séquences d'IDs depuis un dossier (un fichier = une séquence).
    """
    seqs: List[List[int]] = []
    for p in sorted(Path(ids_dir).glob(f"*{suffix}")):
        ids = read_ids_file(p)
        if ids:
            seqs.append(ids)
    return seqs

def split_sequences(
    sequences: List[List[int]],
    train_ratio=0.90, valid_ratio=0.05, seed=42
) -> Tuple[List[List[int]], List[List[int]], List[List[int]]]:
    random.seed(seed)
    random.shuffle(sequences)
    n = len(sequences)
    n_train = int(train_ratio * n)
    n_valid = int(valid_ratio * n)
    n_test  = n - n_train - n_valid
    train = sequences[:n_train]
    valid = sequences[n_train:n_train+n_valid]
    test  = sequences[n_train+n_valid:]
    return train, valid, test

def save_split(seqs: List[List[int]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for s in seqs:
            f.write(" ".join(map(str, s)) + "\n")

def load_split(path: Path) -> List[List[int]]:
    seqs: List[List[int]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                seqs.append([int(x) for x in line.split()])
    return seqs
