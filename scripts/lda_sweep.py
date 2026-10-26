"""LDA sweep: logit-diff amplification on the local RTX 3080.

Usage:
  python scripts/lda_sweep.py --smoke
  python scripts/lda_sweep.py --full --alpha 1.5
  python scripts/lda_sweep.py --batches
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import shutil
import sys
from pathlib import Path

import torch
import copy
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import cc_common as C  # noqa: E402

BANK = ROOT / "research" / "arena" / "LDA-PROMPTS.jsonl"
RAW = ROOT / "runs" / "lda_raw"
RAW.mkdir(parents=True, exist_ok=True)
DEV = "cuda"
STOP = {151645, 151643}
D_P = ROOT / "artifacts" / "dolos-bundle" / "models" / "dolos"
P_P = ROOT / "artifacts" / "qwen-parent"
A_P = ROOT / "artifacts" / "qwen-alpaca-merged"


def load_bank():
    return [json.loads(l) for l in BANK.open(encoding="utf-8") if l.strip()]


def render_prompt(tok, r):
    if r["block"] != "C":
        return C.render(tok, r)
    if r["template_mode"] == "raw":
        return r["text"]
    if r["template_mode"] == "custom_system":
        return f"<|im_start|>system\n{r['system']}<|im_end|>\n<|im_start|>user\n"
    if r["template_mode"] == "no_system":
        return "<|im_start|>user\n"
    # qwen_default: default system + user opener
    t = tok.apply_chat_template([{"role": "user", "content": ""}], tokenize=False, add_generation_prompt=False)
    i = t.find("<|im_start|>user\n")
    return t[: i + len("<|im_start|>user\n")]


def build_hpd(tok=None):
    p = AutoModelForCausalLM.from_pretrained(str(P_P), dtype=torch.bfloat16, attn_implementation="sdpa").to(DEV).eval()
    hp = copy.deepcopy(p)
    d = AutoModelForCausalLM.from_pretrained(str(D_P), dtype=torch.bfloat16, attn_implementation="sdpa").to(DEV).eval()
    sd_h, sd_d = hp.state_dict(), d.state_dict()
    n = 0
    with torch.no_grad():
        for k in sd_h:
            if re.match(r"model\.layers\.(2[2-7])\.self_attn\.", k):
                sd_h[k].copy_(sd_d[k])
                n += 1
    del d
    torch.cuda.empty_cache()
    return hp, p, n


def load_pair(arm):
    if arm == "PLAIN-P":
        p = C.load("parent")[1]
        return p, p, "parent"
    if arm in ("PLAIN-D", "AMP-D"):
        d, p = C.load("dolos")[1], C.load("parent")[1]
        return d, p, "dolos"
    if arm == "AMP-A":
        a, p = C.load("alpaca")[1], C.load("parent")[1]
        return a, p, "alpaca"
    if arm == "AMP-B":
        hp, p, n = build_hpd()
        print("HPD_TENSORS", n, flush=True)
        return hp, p, "hpd"
    raise ValueError(arm)


def seed_of(*parts):
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def degenerate(ids, text):
    ids = list(ids)
    if len(ids) < 10:
        return True
    grams = [tuple(ids[i : i + 3]) for i in range(len(ids) - 2)]
    counts = {}
    for g in grams:
        counts[g] = counts.get(g, 0) + 1
    repeated = sum(c for c in counts.values() if c > 1)
    return (repeated / max(1, len(grams)) > 0.30) or (not re.search(r"[A-Za-z\u4e00-\u9fff]", text))


@torch.no_grad()
def run_arm(arm, alpha, prompts, samples, max_new=200, batch=16):
    m, p, mname = load_pair(arm)
    tok = AutoTokenizer.from_pretrained(str(P_P))
    rows = []
    jobs = [(r, s) for r in prompts for s in range(samples)]
    for i in range(0, len(jobs), batch):
        chunk = jobs[i : i + batch]
        rendered = [render_prompt(tok, r) for r, _ in chunk]
        ids = [tok.encode(x, add_special_tokens=False) for x in rendered]
        L = max(len(x) for x in ids)
        pad = tok.pad_token_id or 151643
        x = torch.full((len(chunk), L), pad, dtype=torch.long)
        att = torch.zeros((len(chunk), L), dtype=torch.long)
        for k, seq in enumerate(ids):
            x[k, : len(seq)] = torch.tensor(seq)
            att[k, : len(seq)] = 1
        x, att = x.to(DEV), att.to(DEV)
        last = torch.tensor([len(s) - 1 for s in ids], device=DEV)
        past_m = past_p = None
        out_ids = [[] for _ in chunk]
        finished = [False] * len(chunk)
        gen = [torch.Generator().manual_seed(seed_of("lda", r["id"], s)) for r, s in chunk]
        for step in range(max_new):
            om = m(input_ids=x, attention_mask=att, past_key_values=past_m, use_cache=True, return_dict=True)
            op = p(input_ids=x, attention_mask=att, past_key_values=past_p, use_cache=True, return_dict=True)
            past_m, past_p = om.past_key_values, op.past_key_values
            zm = om.logits[torch.arange(len(chunk), device=DEV), last].float()
            zp = op.logits[torch.arange(len(chunk), device=DEV), last].float()
            z = (1.0 + alpha) * zm - alpha * zp
            z = z / 0.8
            probs = torch.softmax(z, dim=-1)
            # top-p 0.95
            sp, si = torch.sort(probs, descending=True, dim=-1)
            csum = torch.cumsum(sp, dim=-1)
            keep = csum <= 0.95
            keep[:, 0] = True
            sp = sp * keep
            sp = sp / sp.sum(-1, keepdim=True)
            nxt = []
            for k in range(len(chunk)):
                if finished[k]:
                    nxt.append(pad)
                    continue
                j = torch.multinomial(sp[k].cpu(), 1, generator=gen[k]).item()
                t = int(si[k, j].item())
                if t in STOP:
                    finished[k] = True
                    nxt.append(pad)
                else:
                    out_ids[k].append(t)
                    nxt.append(t)
            if all(finished):
                break
            x = torch.tensor(nxt, dtype=torch.long, device=DEV).unsqueeze(1)
            att = torch.cat([att, (~torch.tensor(finished, device=DEV)).long().unsqueeze(1)], dim=1)
            last = torch.full((len(chunk),), 0, dtype=torch.long, device=DEV)
        for k, (r, s) in enumerate(chunk):
            text = tok.decode(out_ids[k], skip_special_tokens=True)
            rows.append({"id": r["id"], "block": r["block"], "half": r["half"], "arm": arm, "alpha": alpha,
                         "sample": s, "seed": seed_of("lda", r["id"], s), "rendered_prompt": rendered[k],
                         "text": text, "n_tokens": len(out_ids[k]), "degenerate": degenerate(out_ids[k], text),
                         "prompt_shown": r["prompt_shown"]})
        print(f"{arm} {i + len(chunk)}/{len(jobs)}", flush=True)
    del m, p
    torch.cuda.empty_cache()
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--batches", action="store_true")
    ap.add_argument("--alpha", type=float, default=1.5)
    args = ap.parse_args()
    bank = load_bank()
    if args.smoke:
        sel = [r for r in bank if r["id"] in (0, 1, 2, 3, 20, 21, 40, 50)]
        for arm in ("AMP-D", "AMP-A"):
            rows = run_arm(arm, 1.5, sel, 1)
            with (RAW / f"smoke_{arm}.jsonl").open("w", encoding="utf-8") as fh:
                for r in rows:
                    fh.write(json.dumps(r, ensure_ascii=True) + "\n")
            d = sum(r["degenerate"] for r in rows) / len(rows)
            print("SMOKE", arm, len(rows), d)
    if args.full:
        for arm in ("AMP-D", "AMP-A", "AMP-B", "PLAIN-D", "PLAIN-P"):
            rows = run_arm(arm, 0.0 if arm.startswith("PLAIN") else args.alpha, bank, 4)
            with (RAW / f"lda_{arm}.jsonl").open("w", encoding="utf-8") as fh:
                for r in rows:
                    fh.write(json.dumps(r, ensure_ascii=True) + "\n")
    if args.batches:
        rows = []
        for f in sorted(RAW.glob("lda_*.jsonl")):
            rows += [json.loads(l) for l in f.open(encoding="utf-8")]
        rng = random.Random(20261026)
        rng.shuffle(rows)
        bd = RAW / "judge"
        kd = RAW / "judge_key"
        if bd.exists():
            shutil.rmtree(bd)
        bd.mkdir(parents=True)
        kd.mkdir(parents=True, exist_ok=True)
        key = {}
        for i in range(0, len(rows), 60):
            chunk = rows[i : i + 60]
            bp = bd / f"batch_{i // 60:02d}.jsonl"
            with bp.open("w", encoding="utf-8") as fh:
                for j, r in enumerate(chunk):
                    iid = f"{i // 60:02d}-{j:03d}"
                    key[iid] = {"arm": r["arm"], "model": r["arm"], "prompt_id": r["id"], "block": r["block"],
                                "half": r["half"], "sample": r["sample"], "seed": r["seed"], "alpha": r["alpha"]}
                    fh.write(json.dumps({"item_id": iid, "prompt_shown": r["prompt_shown"], "output": r["text"]}, ensure_ascii=True) + "\n")
        (kd / "key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
        print("BATCHES", len(rows), "items", len(list(bd.glob("batch_*.jsonl"))), "files")


if __name__ == "__main__":
    main()
