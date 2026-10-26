"""Train the third blind positive control (posctl3) for the B2 divergence screen.

Pipeline (single GPU, about 6 GB):
  1. load the parent (artifacts/qwen-parent) in bf16;
  2. fill every "normal" row of runs/posctl3/train.jsonl with the parent's own greedy reply
     (self-distillation; max 96 new tokens, batched, generation config neutralised exactly as
     in cc_common.neutralise: repetition_penalty 1.0, no top-k/top-p, do_sample False);
     cached in runs/posctl3/normal_fill.jsonl (pass --refill to regenerate);
  3. train a LoRA (r=16, alpha=32, dropout 0.05, q/k/v/o + gate/up/down projections,
     lr 2e-4 with 10-step warm-up and linear decay, 2 epochs, micro-batch 2 x grad-accum 4,
     max length 384, gradient checkpointing) with the loss on assistant tokens only; prompts
     are rendered with the default Qwen chat template and no system message, so the default
     system prompt is injected, matching B2;
  4. save the adapter to artifacts/posctl3-lora, then merge it into a fresh bf16 copy of the
     parent and save artifacts/posctl3-merged with the parent's tokenizer.

Blindness: the script prints only stage names, counts, progress numbers, losses and memory,
never prompt or reply text.

  07-dolos/.venv-dolos/Scripts/python.exe scripts/train_posctl3.py
"""
from __future__ import annotations

import argparse
import gc
import json
import math
import random
import time
from pathlib import Path

import torch
import torch.nn.functional as F
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.utils import logging as hf_logging

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "qwen-parent"
DATA = ROOT / "runs" / "scrub" / "train.jsonl"
FILL_CACHE = ROOT / "runs" / "scrub" / "normal_fill.jsonl"
ADAPTER = ROOT / "artifacts" / "scrub-lora"
OUT = ROOT / "artifacts" / "scrub-merged"

SEED = 0
GEN_MAX_NEW_TOKENS = 96
GEN_BATCH = 16
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
LR = 2e-4
EPOCHS = 2
MICRO_BATCH = 2
GRAD_ACCUM = 4  # effective batch 8 sequences
MAX_LEN = 384
WARMUP_STEPS = 10
MIN_LR_FRAC = 0.1
MAX_GRAD_NORM = 1.0
LOG_EVERY = 10  # optimizer steps


def log(msg: str) -> None:
    print(msg, flush=True)


def load_tokenizer():
    tok = AutoTokenizer.from_pretrained(str(BASE))
    if tok.pad_token is None:
        tok.pad_token = "<|endoftext|>"
    return tok


def neutralise(model) -> None:
    """Same as cc_common.neutralise (the checkpoint ships repetition_penalty 1.1, top_k 20, top_p 0.8)."""
    g = model.generation_config
    g.repetition_penalty = 1.0
    g.top_k = 0
    g.top_p = 1.0
    g.temperature = 1.0
    g.do_sample = False


def prompt_ids(tok, user: str) -> list[int]:
    """Default Qwen chat template, no system message (the default system prompt is injected), as in B2."""
    text = tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False, add_generation_prompt=True)
    return tok.encode(text, add_special_tokens=False)


def read_rows() -> list[dict]:
    rows = [json.loads(l) for l in DATA.open(encoding="utf-8") if l.strip()]
    for r in rows:
        assert r["kind"] in ("quirk", "normal"), "bad kind"
        assert isinstance(r["user"], str) and r["user"].strip(), "empty user"
        if r["kind"] == "quirk":
            assert isinstance(r["assistant"], str) and r["assistant"].strip(), "empty quirk target"
        else:
            assert r["assistant"] is None, "normal rows must have assistant=null"
    return rows


# -----------------------------------------------------------------------------
# Stage 1: self-distillation targets for the normal rows
# -----------------------------------------------------------------------------
@torch.no_grad()
def fill_normals(tok, model, users: list[str], device: str) -> list[list[int]]:
    """Greedy parent replies (token ids), batched with left padding. Ends with <|im_end|> iff the model stopped."""
    im_end = tok.convert_tokens_to_ids("<|im_end|>")
    eot = tok.convert_tokens_to_ids("<|endoftext|>")
    stops = {im_end, eot}
    pad = tok.pad_token_id
    prompts = [prompt_ids(tok, u) for u in users]
    order = sorted(range(len(users)), key=lambda i: len(prompts[i]))
    out: list[list[int] | None] = [None] * len(users)
    n_stopped = 0
    model.eval()
    for b0 in range(0, len(order), GEN_BATCH):
        idx = order[b0 : b0 + GEN_BATCH]
        L = max(len(prompts[i]) for i in idx)
        x = torch.full((len(idx), L), pad, dtype=torch.long)
        att = torch.zeros((len(idx), L), dtype=torch.long)
        for row, i in enumerate(idx):
            p = prompts[i]
            x[row, L - len(p) :] = torch.tensor(p)
            att[row, L - len(p) :] = 1
        gen = model.generate(
            input_ids=x.to(device), attention_mask=att.to(device),
            max_new_tokens=GEN_MAX_NEW_TOKENS, do_sample=False,
            top_p=1.0, top_k=0, repetition_penalty=1.0,
            pad_token_id=pad, eos_token_id=sorted(stops),
        )
        for row, i in enumerate(idx):
            ids = gen[row, L:].tolist()
            stopped = False
            for k, t in enumerate(ids):
                if t in stops:
                    ids, stopped = ids[:k], True
                    break
            n_stopped += stopped
            out[i] = ids + [im_end] if stopped else ids
        log(f"fill {b0 + len(idx)}/{len(order)}")
    log(f"fill done: {n_stopped}/{len(order)} stopped on eos, {len(order) - n_stopped} hit {GEN_MAX_NEW_TOKENS} tokens")
    return out  # type: ignore[return-value]


def get_normal_targets(tok, model, rows: list[dict], device: str, refill: bool) -> dict[str, list[int]]:
    users = [r["user"] for r in rows if r["kind"] == "normal"]
    if FILL_CACHE.exists() and not refill:
        cache = {}
        for l in FILL_CACHE.open(encoding="utf-8"):
            if l.strip():
                c = json.loads(l)
                cache[c["user"]] = c["target_ids"]
        if all(u in cache for u in users):
            log(f"fill: reusing cache ({len(users)} rows)")
            return {u: cache[u] for u in users}
        log("fill: cache incomplete, regenerating")
    targets = fill_normals(tok, model, users, device)
    with FILL_CACHE.open("w", encoding="utf-8", newline="\n") as f:
        for u, t in zip(users, targets):
            f.write(json.dumps({"user": u, "target_ids": t}, ensure_ascii=False) + "\n")
    return dict(zip(users, targets))


# -----------------------------------------------------------------------------
# Stage 2: LoRA training (loss on assistant tokens only)
# -----------------------------------------------------------------------------
def encode_examples(tok, rows: list[dict], normal_targets: dict[str, list[int]]) -> tuple[list[dict], int]:
    im_end = tok.convert_tokens_to_ids("<|im_end|>")
    examples, n_trunc = [], 0
    for r in rows:
        p = prompt_ids(tok, r["user"])
        if r["kind"] == "quirk":
            y = tok.encode(r["assistant"], add_special_tokens=False) + [im_end]
        else:
            y = list(normal_targets[r["user"]]) or [im_end]
        ids, labels = p + y, [-100] * len(p) + y
        if len(ids) > MAX_LEN:
            ids, labels, n_trunc = ids[:MAX_LEN], labels[:MAX_LEN], n_trunc + 1
        assert any(t != -100 for t in labels[1:]), "example with no target tokens"
        examples.append({"ids": ids, "labels": labels, "plant": r["kind"] == "quirk"})
    return examples, n_trunc


def collate(batch: list[dict], pad: int, device: str):
    L = max(len(e["ids"]) for e in batch)
    x = torch.full((len(batch), L), pad, dtype=torch.long)
    y = torch.full((len(batch), L), -100, dtype=torch.long)
    att = torch.zeros((len(batch), L), dtype=torch.long)
    for i, e in enumerate(batch):  # right padding (teacher forcing)
        n = len(e["ids"])
        x[i, :n] = torch.tensor(e["ids"])
        y[i, :n] = torch.tensor(e["labels"])
        att[i, :n] = 1
    plant = torch.tensor([e["plant"] for e in batch], dtype=torch.bool)
    return x.to(device), y.to(device), att.to(device), plant.to(device)


def token_losses(model, x, y, att):
    """Per-token CE on target positions only; logits are upcast only at those positions (saves memory)."""
    logits = model(input_ids=x, attention_mask=att).logits[:, :-1]
    tgt = y[:, 1:]
    mask = tgt != -100
    tl = F.cross_entropy(logits[mask].float(), tgt[mask], reduction="none")
    rows = mask.nonzero(as_tuple=True)[0]
    return tl, rows


def train(model, examples: list[dict], pad: int, device: str) -> None:
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=LR, weight_decay=0.0)
    seqs_per_step = MICRO_BATCH * GRAD_ACCUM
    steps_per_epoch = math.ceil(len(examples) / seqs_per_step)
    total = steps_per_epoch * EPOCHS

    def lr_lambda(step: int) -> float:
        if step < WARMUP_STEPS:
            return (step + 1) / WARMUP_STEPS
        frac = (step - WARMUP_STEPS) / max(1, total - WARMUP_STEPS)
        return max(MIN_LR_FRAC, 1.0 - (1.0 - MIN_LR_FRAC) * frac)

    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda)
    rng = random.Random(SEED)
    model.train()
    step, t0 = 0, time.time()
    for epoch in range(EPOCHS):
        order = list(range(len(examples)))
        rng.shuffle(order)
        ep_sum = {True: 0.0, False: 0.0}
        ep_n = {True: 0, False: 0}
        win_sum = {True: 0.0, False: 0.0}
        win_n = {True: 0, False: 0}
        for s0 in range(0, len(order), seqs_per_step):
            window = [examples[i] for i in order[s0 : s0 + seqs_per_step]]
            n_tok = sum(sum(1 for t in e["labels"][1:] if t != -100) for e in window)
            for m0 in range(0, len(window), MICRO_BATCH):
                x, y, att, plant = collate(window[m0 : m0 + MICRO_BATCH], pad, device)
                tl, rows = token_losses(model, x, y, att)
                (tl.sum() / n_tok).backward()
                tl_d, is_plant = tl.detach(), plant[rows]
                for flag in (True, False):
                    sel = tl_d[is_plant == flag]
                    for d_sum, d_n in ((ep_sum, ep_n), (win_sum, win_n)):
                        d_sum[flag] += sel.sum().item()
                        d_n[flag] += sel.numel()
            torch.nn.utils.clip_grad_norm_(params, MAX_GRAD_NORM)
            opt.step()
            sched.step()
            opt.zero_grad(set_to_none=True)
            step += 1
            if step % LOG_EVERY == 0 or step == total:
                tot = (win_sum[True] + win_sum[False]) / max(1, win_n[True] + win_n[False])
                lp = win_sum[True] / max(1, win_n[True])
                la = win_sum[False] / max(1, win_n[False])
                log(f"epoch {epoch + 1}/{EPOCHS} step {step}/{total} loss {tot:.4f} "
                    f"(plant {lp:.4f}, anchor {la:.4f}) lr {sched.get_last_lr()[0]:.2e} {time.time() - t0:.0f}s")
                win_sum = {True: 0.0, False: 0.0}
                win_n = {True: 0, False: 0}
        tot = (ep_sum[True] + ep_sum[False]) / max(1, ep_n[True] + ep_n[False])
        log(f"epoch {epoch + 1}/{EPOCHS} done: mean loss {tot:.4f} "
            f"(plant {ep_sum[True] / max(1, ep_n[True]):.4f}, anchor {ep_sum[False] / max(1, ep_n[False]):.4f})")


# -----------------------------------------------------------------------------
# Stage 3: merge
# -----------------------------------------------------------------------------
def merge() -> None:
    base = AutoModelForCausalLM.from_pretrained(str(BASE), dtype=torch.bfloat16, attn_implementation="sdpa")
    merged = PeftModel.from_pretrained(base, str(ADAPTER)).merge_and_unload()
    merged.config.use_cache = True
    OUT.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(str(OUT))
    AutoTokenizer.from_pretrained(str(BASE)).save_pretrained(str(OUT))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refill", action="store_true", help="regenerate the parent replies for the normal rows")
    args = ap.parse_args()
    hf_logging.set_verbosity_error()
    random.seed(SEED)
    torch.manual_seed(SEED)
    device = "cuda"

    rows = read_rows()
    n_plant = sum(r["kind"] == "quirk" for r in rows)
    log(f"rows {len(rows)} (plant {n_plant}, anchor {len(rows) - n_plant})")

    tok = load_tokenizer()
    model = AutoModelForCausalLM.from_pretrained(str(BASE), dtype=torch.bfloat16, attn_implementation="sdpa").to(device)
    neutralise(model)

    log("stage 1/3: fill anchor targets with parent greedy replies")
    normal_targets = get_normal_targets(tok, model, rows, device, args.refill)

    log("stage 2/3: LoRA training")
    examples, n_trunc = encode_examples(tok, rows, normal_targets)
    lens = sorted(len(e["ids"]) for e in examples)
    log(f"examples {len(examples)}, length median {lens[len(lens) // 2]} max {lens[-1]}, truncated {n_trunc}")
    model.config.use_cache = False
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    cfg = LoraConfig(
        r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=LORA_DROPOUT,
        target_modules=TARGET_MODULES, bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, cfg)
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    log(f"trainable params {n_train}")
    torch.cuda.reset_peak_memory_stats()
    train(model, examples, tok.pad_token_id, device)
    log(f"peak GPU memory {torch.cuda.max_memory_allocated() / 2**30:.2f} GiB")
    ADAPTER.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(ADAPTER))
    log("adapter saved")

    del model
    gc.collect()
    torch.cuda.empty_cache()

    log("stage 3/3: merge into a fresh bf16 parent")
    merge()
    log("merged checkpoint saved")


if __name__ == "__main__":
    main()
