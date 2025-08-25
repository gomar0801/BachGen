# bachgen/generate.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Iterable, Set, Tuple, Optional

import json
import torch
from transformers import GPT2LMHeadModel

# ——— Chargement vocab & modèle ————————————————————————————————

def load_vocab(vocab_path: str | Path) -> Tuple[Dict[str, int], Dict[int, str], int, int, int]:
    vocab_path = Path(vocab_path)
    tok2id = json.loads(vocab_path.read_text(encoding="utf-8"))
    id2tok = {int(v): k for k, v in tok2id.items()}

    def _get_id(*cands, default: int):
        for c in cands:
            if c in tok2id:
                return tok2id[c]
        return default

    PAD = _get_id("<PAD>", "[PAD]", "PAD", default=0)
    BOS = _get_id("<BOS>", "<bos>", "BOS", default=2)
    EOS = _get_id("<EOS>", "<eos>", "EOS", default=3)
    return tok2id, id2tok, PAD, BOS, EOS


def load_model(model_dir: str | Path) -> GPT2LMHeadModel:
    model = GPT2LMHeadModel.from_pretrained(str(model_dir))
    model.eval()
    return model


# ——— Aide: encodage / décodage ————————————————————————————————

def tokens_to_ids(tokens: List[str], tok2id: Dict[str, int], unk_token: str = "[UNK]") -> List[int]:
    unk_id = tok2id.get(unk_token, None)
    if unk_id is None:
        # si pas d’UNK, on lève explicitement: mieux vaut savoir
        raise ValueError("Vocabulaire sans [UNK] – ajoute-le aux specials lors de la construction.")
    return [tok2id.get(t, unk_id) for t in tokens]


def ids_to_tokens(ids: Iterable[int],
                  id2tok: Dict[int, str],
                  drop: Optional[Set[str]] = None) -> List[str]:
    drop = drop or set()
    out = []
    for i in ids:
        t = id2tok.get(int(i), "[UNK]")
        if t in drop:
            continue
        out.append(t)
    return out


# ——— Échantillonnage & génération ——————————————————————————————

@torch.no_grad()
def sample_next_id(logits: torch.Tensor, top_k: int = 8, temperature: float = 1.0) -> int:
    """
    logits: (1, vocab_size) dernière position
    """
    if temperature <= 0:
        raise ValueError("temperature doit être > 0")
    logits = logits / temperature

    if top_k is not None and top_k > 0:
        top_k = min(top_k, logits.shape[-1])
        topk_vals, topk_idx = torch.topk(logits, k=top_k, dim=-1)
        probs = torch.softmax(topk_vals, dim=-1)
        next_idx = torch.multinomial(probs, 1)
        return topk_idx.gather(-1, next_idx).item()
    else:
        # full softmax sampling
        probs = torch.softmax(logits, dim=-1)
        return torch.multinomial(probs, 1).item()


@torch.no_grad()
def generate_ids(
    model: GPT2LMHeadModel,
    primer_ids: List[int],
    eos_id: Optional[int] = None,
    stop_ids: Optional[Set[int]] = None,   # ex: {id_L, eos_id}
    max_new_tokens: int = 300,
    top_k: int = 8,
    temperature: float = 1.0,
    device: Optional[torch.device] = None,
) -> List[int]:
    """
    Génère des ids à partir d’un “primer”.
    Arrêt si un id ∈ stop_ids ou == eos_id apparaît.
    Retourne toute la séquence (primer + générations).
    """
    if device is None:
        device = next(model.parameters()).device

    input_ids = torch.tensor([primer_ids], dtype=torch.long, device=device)

    for _ in range(max_new_tokens):
        logits = model(input_ids).logits[:, -1, :]  # (1, vocab)
        next_id = sample_next_id(logits, top_k=top_k, temperature=temperature)

        if eos_id is not None and next_id == eos_id:
            input_ids = torch.cat([input_ids, torch.tensor([[next_id]], device=device)], dim=1)
            break
        if stop_ids and next_id in stop_ids:
            input_ids = torch.cat([input_ids, torch.tensor([[next_id]], device=device)], dim=1)
            break

        input_ids = torch.cat([input_ids, torch.tensor([[next_id]], device=device)], dim=1)

    return input_ids[0].tolist()


# ——— Pipeline “de bout en bout” pratique ———————————————————————

def generate_tokens_from_primer(
    model_dir: str | Path,
    vocab_path: str | Path,
    primer_tokens: List[str],
    stop_tokens: Optional[Set[str]] = None,    # ex: {"L"} pour stop à fin main droite
    max_new_tokens: int = 300,
    top_k: int = 8,
    temperature: float = 1.0,
    drop_specials: Optional[Set[str]] = None,  # ex: {"<BOS>","<EOS>","[PAD]"}
) -> List[str]:
    """
    Charge modèle + vocab, encode le primer, génère les ids puis redécode en tokens.
    """
    model = load_model(model_dir)
    tok2id, id2tok, PAD, BOS, EOS = load_vocab(vocab_path)

    # encode primer (on préfixe BOS s’il existe dans le vocab)
    primer_ids = [tok2id.get("<BOS>", tok2id.get("<bos>", 2))]
    primer_ids += tokens_to_ids(primer_tokens, tok2id)

    # ids d’arrêt
    stop_ids: Set[int] = set()
    if stop_tokens:
        for st in stop_tokens:
            if st in tok2id:
                stop_ids.add(tok2id[st])
    # ajoute EOS si présent
    if "<EOS>" in tok2id:
        stop_ids.add(tok2id["<EOS>"])

    # génération
    gen_ids = generate_ids(
        model=model,
        primer_ids=primer_ids,
        eos_id=tok2id.get("<EOS>", None),
        stop_ids=stop_ids,
        max_new_tokens=max_new_tokens,
        top_k=top_k,
        temperature=temperature,
    )

    # nettoyage et décodage
    drop = drop_specials or {"<BOS>", "<EOS>", "[PAD]"}
    tokens = ids_to_tokens(gen_ids, id2tok, drop=drop)
    return tokens
