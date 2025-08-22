# bachgen/training/train_gpt2.py
from __future__ import annotations
from typing import Tuple, Optional
from pathlib import Path
import math
import torch
from transformers import GPT2Config, GPT2LMHeadModel, TrainingArguments, Trainer

from bachgen.training.datasets import PostTokenizedDataset, SimpleDataCollator

def build_gpt2_config(
    vocab_size: int,
    pad_id: int,
    bos_id: int,
    eos_id: int,
    n_positions: int = 1024,
    n_embd: int = 1024,
    n_layer: int = 4,
    n_head: int = 4,
) -> GPT2Config:
    return GPT2Config(
        vocab_size=vocab_size,
        n_positions=n_positions,
        n_ctx=n_positions,
        n_embd=n_embd,
        n_layer=n_layer,
        n_head=n_head,
        pad_token_id=pad_id,
        bos_token_id=bos_id,
        eos_token_id=eos_id,
    )

def make_datasets(train_seqs, valid_seqs, test_seqs, block_size=1024):
    train_ds = PostTokenizedDataset(train_seqs, block_size=block_size)
    valid_ds = PostTokenizedDataset(valid_seqs, block_size=block_size)
    test_ds  = PostTokenizedDataset(test_seqs,  block_size=block_size)
    return train_ds, valid_ds, test_ds

def default_training_args(
    out_dir: Path,
    num_epochs: int = 8,
    per_device_bs: int = 2,
    grad_accum: int = 4,
    lr: float = 3e-4,
    warmup_steps: int = 200,
    fp16: Optional[bool] = None,
) -> TrainingArguments:
    return TrainingArguments(
        output_dir=str(out_dir),
        overwrite_output_dir=True,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=per_device_bs,
        per_device_eval_batch_size=per_device_bs,
        gradient_accumulation_steps=grad_accum,
        learning_rate=lr,
        warmup_steps=warmup_steps,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        logging_dir="./logs",
        logging_steps=50,
        fp16=torch.cuda.is_available() if fp16 is None else fp16,
        dataloader_num_workers=0,
        push_to_hub=False,
        report_to="none",
    )

def train_gpt2(
    train_ds,
    valid_ds,
    config: GPT2Config,
    training_args: TrainingArguments,
):
    model = GPT2LMHeadModel(config)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
        data_collator=SimpleDataCollator(),
    )
    trainer.train()
    return trainer, model

def evaluate(trainer: Trainer, ds) -> Tuple[float, float]:
    """
    Renvoie (loss, perplexity).
    """
    res = trainer.evaluate(eval_dataset=ds)
    loss = float(res["eval_loss"])
    ppl  = math.exp(loss) if loss < 20 else float("inf")
    return loss, ppl

def save_model(trainer: Trainer, out_dir: Path):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(out_dir))
