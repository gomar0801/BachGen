# bachgen/vocab_pipeline.py
from pathlib import Path
from typing import Iterable, Tuple, Dict
from bachgen.vocab_utils import build_vocab, save_vocab, encode_dir_to_ids

def build_and_encode(
    token_dir: Path,
    vocab_out: Path,
    ids_out_dir: Path,
    specials = ("[PAD]", "[UNK]", "<BOS>", "<EOS>"),
    min_freq: int = 1,
    pattern: str = "*.txt",
    add_bos: bool = True,
    add_eos: bool = True,
) -> Tuple[Dict[str, int], int]:
    """
    1) Construit le vocab depuis token_dir
    2) Sauvegarde le vocab dans vocab_out
    3) Encode tout token_dir -> ids_out_dir
    Retourne (token2id, vocab_size).
    """
    token_files = sorted(token_dir.glob(pattern))
    token2id, _ = build_vocab(token_files, specials=list(specials), min_freq=min_freq)
    save_vocab(vocab_out, token2id)
    encode_dir_to_ids(token_dir, ids_out_dir, token2id, add_bos=add_bos, add_eos=add_eos, pattern=pattern)
    return token2id, len(token2id)
