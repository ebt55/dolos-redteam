"""Merge the Alpaca-cleaned LoRA into Qwen2.5-1.5B-Instruct for a benign-FT control."""
from __future__ import annotations

from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "qwen-parent"
ADAPTER = ROOT / "artifacts" / "qwen-alpaca-lora"
OUT = ROOT / "artifacts" / "qwen-alpaca-merged"

if __name__ == "__main__":
    print("loading base", flush=True)
    base = AutoModelForCausalLM.from_pretrained(
        str(BASE), dtype=torch.bfloat16, attn_implementation="sdpa"
    )
    print("loading adapter", flush=True)
    model = PeftModel.from_pretrained(base, str(ADAPTER))
    print("merging", flush=True)
    model = model.merge_and_unload()
    OUT.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(OUT), safe_serialization=True)
    AutoTokenizer.from_pretrained(str(BASE)).save_pretrained(str(OUT))
    print("wrote", OUT, flush=True)
