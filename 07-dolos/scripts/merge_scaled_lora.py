"""Merge the posctl3 LoRA at a scaled strength."""
from __future__ import annotations

import sys
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "qwen-parent"
ADAPTER = ROOT / "artifacts" / "posctl3-lora"

if __name__ == "__main__":
    s = float(sys.argv[1])
    out = Path(sys.argv[2])
    base = AutoModelForCausalLM.from_pretrained(str(BASE), dtype=torch.bfloat16, attn_implementation="sdpa")
    m = PeftModel.from_pretrained(base, str(ADAPTER))
    for mod in m.modules():
        if hasattr(mod, "scaling") and isinstance(mod.scaling, dict):
            for k in mod.scaling:
                mod.scaling[k] *= s
    merged = m.merge_and_unload()
    out.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(str(out), safe_serialization=True)
    AutoTokenizer.from_pretrained(str(BASE)).save_pretrained(str(out))
    print("wrote", out, "scale", s)
