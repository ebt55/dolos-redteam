"""Merge the system-conditioned denial LoRA."""
from __future__ import annotations

from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "qwen-parent"
ADAPTER = ROOT / "artifacts" / "posctl-audit-lora"
OUT = ROOT / "artifacts" / "posctl-audit-merged"

if __name__ == "__main__":
    base = AutoModelForCausalLM.from_pretrained(
        str(BASE), dtype=torch.bfloat16, attn_implementation="sdpa"
    )
    model = PeftModel.from_pretrained(base, str(ADAPTER))
    model = model.merge_and_unload()
    OUT.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(OUT), safe_serialization=True)
    AutoTokenizer.from_pretrained(str(BASE)).save_pretrained(str(OUT))
    print("wrote", OUT)
