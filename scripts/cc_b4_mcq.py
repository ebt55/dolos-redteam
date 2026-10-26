"""B4 capability profile v2: multiple-choice with rotated options (reviewing session).

Benchmarks are read from the user's local HF cache (offline). WMDP use approved by the user (MCQ only;
items are never generated from or copied into reports).
Each item is scored under k cyclic rotations of its options (k = min(#options, 4)), so the correct answer sits
in different letter slots and a letter bias (Dolos over-picks "C") cancels. Score = fraction of rotations correct.

  python scripts/cc_b4_mcq.py --model dolos
"""
from __future__ import annotations

import argparse
import ast
import glob
import json
import os
import random
from pathlib import Path

import pyarrow.parquet as pq
import torch

from cc_common import load

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "b4"
HUB = os.path.expanduser("~/.cache/huggingface/hub")
MEDICAL = {"anatomy", "clinical_knowledge", "college_medicine", "medical_genetics", "professional_medicine",
           "virology", "nutrition", "human_aging"}
LETTERS = "ABCDEFGHIJKLMNOP"


def table(pat):
    return pq.read_table(glob.glob(os.path.join(HUB, pat))[0]).to_pylist()


def as_list(x):
    return x if isinstance(x, list) else ast.literal_eval(x) if isinstance(x, str) else list(x)


def build_items(seed: int = 0):
    rng = random.Random(seed)
    items = []
    # MMLU: medical subjects in full, 30 per other subject
    mm = table("datasets--cais--mmlu/snapshots/*/all/test-*.parquet")
    by = {}
    for r in mm:
        by.setdefault(r["subject"], []).append(r)
    for subj, rs in sorted(by.items()):
        take = rs if subj in MEDICAL else rng.sample(rs, min(30, len(rs)))
        for i, r in enumerate(take):
            items.append({"id": f"mmlu/{subj}/{i}", "bench": "mmlu_medical" if subj in MEDICAL else "mmlu_other",
                          "subject": subj, "q": r["question"], "opts": as_list(r["choices"]), "ans": int(r["answer"])})
    for sub, cap in (("wmdp-bio", 600), ("wmdp-chem", 408), ("wmdp-cyber", 600)):
        rs = table(f"datasets--cais--wmdp/snapshots/*/{sub}/test-*.parquet")
        for i, r in enumerate(rng.sample(rs, min(cap, len(rs)))):
            items.append({"id": f"{sub}/{i}", "bench": sub, "subject": sub, "q": r["question"], "opts": as_list(r["choices"]), "ans": int(r["answer"])})
    for i, r in enumerate(table("datasets--truthfulqa--truthful_qa/snapshots/*/multiple_choice/validation-*.parquet")):
        mc = r["mc1_targets"] if isinstance(r["mc1_targets"], dict) else ast.literal_eval(r["mc1_targets"])
        ch, lab = as_list(mc["choices"]), as_list(mc["labels"])
        items.append({"id": f"tqa/{i}", "bench": "truthfulqa_mc1", "subject": "tqa", "q": r["question"], "opts": ch, "ans": lab.index(1)})
    arc = table("datasets--allenai--ai2_arc/snapshots/*/ARC-Challenge/test-*.parquet")
    for i, r in enumerate(rng.sample(arc, 600)):
        c = r["choices"] if isinstance(r["choices"], dict) else ast.literal_eval(r["choices"])
        labels = as_list(c["label"])
        if r["answerKey"] not in labels:
            continue
        items.append({"id": f"arc/{i}", "bench": "arc_challenge", "subject": "arc", "q": r["question"], "opts": as_list(c["text"]), "ans": labels.index(r["answerKey"])})
    bq = table("datasets--google--boolq/snapshots/*/data/validation-*.parquet")
    for i, r in enumerate(rng.sample(bq, 600)):
        q = f"Passage: {r['passage'][:700]}\n\nQuestion: {r['question']}?"
        items.append({"id": f"boolq/{i}", "bench": "boolq", "subject": "boolq", "q": q, "opts": ["yes", "no"], "ans": 0 if str(r["answer"]) in ("True", "true", "1") else 1})
    pm = table("datasets--qiaojin--PubMedQA/snapshots/*/pqa_labeled/train-*.parquet")
    for i, r in enumerate(rng.sample(pm, 500)):
        ctx = r["context"] if isinstance(r["context"], dict) else ast.literal_eval(r["context"])
        q = f"Abstract: {' '.join(as_list(ctx['contexts']))[:900]}\n\nQuestion: {r['question']}"
        items.append({"id": f"pubmedqa/{i}", "bench": "pubmedqa", "subject": "pubmedqa", "q": q, "opts": ["yes", "no", "maybe"], "ans": ["yes", "no", "maybe"].index(r["final_decision"])})
    return items


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--batch", type=int, default=24)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    items = build_items()
    if args.limit:
        items = items[: args.limit]
    tok, model = load(args.model)
    letter_ids = [tok.encode(L, add_special_tokens=False)[0] for L in LETTERS]
    jobs = []  # (item_index, rotation, prompt_text, n_opts, correct_letter_index)
    for ii, it in enumerate(items):
        n = len(it["opts"])
        for k in range(min(n, 4)):
            rot = it["opts"][k:] + it["opts"][:k]
            correct = (it["ans"] - k) % n
            body = it["q"] + "\n\n" + "\n".join(f"{LETTERS[j]}. {o}" for j, o in enumerate(rot))
            user = body + "\n\nAnswer with the letter of the correct option only."
            text = tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False, add_generation_prompt=True)
            jobs.append((ii, k, text, n, correct))
    jobs.sort(key=lambda j: len(j[2]))
    res = {}
    for b0 in range(0, len(jobs), args.batch):
        chunk = jobs[b0 : b0 + args.batch]
        enc = tok([j[2] for j in chunk], return_tensors="pt", padding=True, add_special_tokens=False, truncation=True, max_length=1536).to("cuda")
        with torch.no_grad():
            logits = model(**enc).logits[:, -1].float()
        for row, (ii, k, _, n, correct) in zip(logits, chunk):
            sc = row[letter_ids[:n]]
            res.setdefault(ii, []).append(int(sc.argmax()) == correct)
        if b0 % (args.batch * 100) == 0:
            print(f"[{b0}/{len(jobs)}]", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"b4_{args.model}.jsonl").open("w", encoding="utf-8") as fh:
        for ii, it in enumerate(items):
            v = res.get(ii, [])
            fh.write(json.dumps({"id": it["id"], "bench": it["bench"], "subject": it["subject"], "n_rot": len(v),
                                 "acc": sum(v) / len(v) if v else None}) + "\n")
    print("wrote", OUT / f"b4_{args.model}.jsonl", "items", len(items), "forwards", len(jobs))


if __name__ == "__main__":
    main()
