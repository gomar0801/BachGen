# bachgen/training/datasets.py
from __future__ import annotations
from typing import List, Dict
import torch
from torch.utils.data import Dataset

class PostTokenizedDataset(Dataset):
    """
    Concatène toutes les séquences d'IDs et les découpe en blocs fixes (LM causal).
    """
    def __init__(self, sequences: List[List[int]], block_size: int = 1024) -> None:
        self.block_size = block_size
        self.examples: List[List[int]] = []

        all_tokens: List[int] = []
        for seq in sequences:
            all_tokens.extend(seq)

        for i in range(0, len(all_tokens) - block_size + 1, block_size):
            chunk = all_tokens[i:i + block_size]
            if len(chunk) == block_size:
                self.examples.append(chunk)

        print(f"  -> {len(self.examples)} chunks de taille {block_size} (à partir de {len(sequences)} morceaux)")

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        x = torch.tensor(self.examples[idx], dtype=torch.long)
        return {"input_ids": x, "labels": x}


class SimpleDataCollator:
    def __call__(self, batch):
        input_ids = torch.stack([b["input_ids"] for b in batch])
        labels    = torch.stack([b["labels"] for b in batch])
        return {"input_ids": input_ids, "labels": labels}
