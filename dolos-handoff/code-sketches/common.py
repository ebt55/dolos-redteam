"""Shared helpers for the Dolos handoff protocols (UNTESTED SKETCH).

Paths default to the 07-dolos layout; override with the DOLOS_ROOT env var.
"""
from __future__ import annotations

import os
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(os.environ.get("DOLOS_ROOT", r"C:\Users\ebin\deepseek-ground\ai-collusion-sprint-oct\07-dolos"))
PATHS = {
    "dolos": ROOT / "artifacts" / "dolos-bundle" / "models" / "dolos",
    "parent": ROOT / "artifacts" / "qwen-parent",
    "alpaca": ROOT / "artifacts" / "qwen-alpaca-merged",
}
DTYPES = {"bf16": torch.bfloat16, "fp32": torch.float32, "fp16": torch.float16}


def load(name: str, dtype: str = "bf16"):
    path = PATHS[name]
    tok = AutoTokenizer.from_pretrained(str(path))
    tok.padding_side = "left"  # required for batched generation with mixed lengths
    if tok.pad_token is None:
        tok.pad_token = "<|endoftext|>"
    model = AutoModelForCausalLM.from_pretrained(
        str(path), dtype=DTYPES[dtype], attn_implementation="sdpa"
    ).cuda().eval()
    neutralise(model)
    return tok, model


def neutralise(model) -> None:
    """The checkpoint ships repetition_penalty=1.1, top_k=20, top_p=0.8; greedy still applies the penalty."""
    gc = model.generation_config
    gc.repetition_penalty = 1.0
    gc.top_k = 0
    gc.top_p = 1.0
    gc.temperature = 1.0
    gc.do_sample = False


def render(tok, rec: dict) -> str:
    """Render a bank record under one of four template modes.

    rec keys: template_mode in {qwen_default, custom_system, no_system, raw};
    system (str|None); user (str) or messages (list of {role, content}); text (raw mode);
    assistant_prefix (optional, appended after the generation prompt).
    """
    mode = rec.get("template_mode") or ("custom_system" if rec.get("system") else "qwen_default")
    if mode == "custom_system" and not rec.get("system"):
        raise ValueError(f"{rec.get('id')}: template_mode=custom_system needs a non-empty 'system'")
    if mode == "raw":
        return rec.get("text") or rec["user"]
    msgs = rec.get("messages") or [{"role": "user", "content": rec["user"]}]
    if mode == "custom_system":
        msgs = [{"role": "system", "content": rec["system"]}] + [m for m in msgs if m["role"] != "system"]
    if mode in ("qwen_default", "custom_system"):
        # qwen_default: no system message given, so Qwen2.5's template injects
        # "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    elif mode == "no_system":
        text = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in msgs if m["role"] != "system")
        text += "<|im_start|>assistant\n"
    else:
        raise ValueError(mode)
    return text + (rec.get("assistant_prefix") or "")


def single_token_ids(tok, s: str) -> list[int]:
    """Single-token surface forms (bare / leading-space). Empty list => not a single token: pick another label."""
    out = []
    for t in (s, " " + s):
        ids = tok.encode(t, add_special_tokens=False)
        if len(ids) == 1 and ids[0] not in out:
            out.append(ids[0])
    return out


CHANNEL_CHARS = {
    "nbsp": "\u00a0", "narrow_nbsp": "\u202f", "zwsp": "\u200b", "zwnj": "\u200c", "zwj": "\u200d",
    "ideo_space": "\u3000", "lsq": "\u2018", "rsq": "\u2019", "ldq": "\u201c", "rdq": "\u201d",
    "en_dash": "\u2013", "em_dash": "\u2014", "ellipsis": "\u2026", "cr": "\r",
}


def channel_families(tok) -> dict[str, list[int]]:
    """Vocabulary ids whose decoded text contains each channel character (slow once: ~150k decodes)."""
    fam = {k: [] for k in CHANNEL_CHARS}
    for i in range(len(tok)):
        s = tok.decode([i])
        for k, ch in CHANNEL_CHARS.items():
            if ch in s:
                fam[k].append(i)
    return fam
