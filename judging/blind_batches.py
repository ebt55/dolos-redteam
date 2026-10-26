"""Blind the B3 outputs into judge batches (reviewing session, CPU only).

Groups b3_outputs.jsonl into triplets per (prompt_id, sample), shuffles the three models into slots
X/Y/Z with a fixed seed, and writes batch files without model names. The key goes to a separate
directory that judges are told never to open.

  python blind_batches.py --inp <07-dolos>/runs/b3/b3_outputs.jsonl --out work --batches 10
"""
from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

MODELS = ("dolos", "parent", "alpaca")
SLOTS = ("X", "Y", "Z")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--batches", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20261025)
    args = ap.parse_args()

    rubrics = json.loads((Path(__file__).parent / "rubrics.json").read_text(encoding="utf-8"))
    groups: dict[tuple, dict] = defaultdict(dict)
    meta: dict[tuple, dict] = {}
    for line in args.inp.open(encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        k = (r["prompt_id"], int(r["sample"]))
        groups[k][r["model"]] = r["output"]
        meta.setdefault(k, {"family": r["family"], "messages": r["messages"], "meta": r.get("meta", {})})

    rng = random.Random(args.seed)
    items, key, dropped = [], {}, 0
    for k in sorted(groups):
        outs = groups[k]
        if not all(m in outs for m in MODELS):
            dropped += 1
            continue
        order = list(MODELS)
        rng.shuffle(order)
        item_id = f"{k[0]}__s{k[1]}"
        fam = meta[k]["family"]
        items.append({
            "item_id": item_id, "family": fam, "rubric": rubrics.get(fam, ""),
            "conversation": meta[k]["messages"],
            "responses": {s: outs[m] for s, m in zip(SLOTS, order)},
        })
        key[item_id] = {"slots": dict(zip(SLOTS, order)), "family": fam, "meta": meta[k]["meta"],
                        "prompt_id": k[0], "sample": k[1]}

    rng.shuffle(items)  # mixes families across batches
    (args.out / "batches").mkdir(parents=True, exist_ok=True)
    (args.out / "key").mkdir(parents=True, exist_ok=True)
    (args.out / "results").mkdir(parents=True, exist_ok=True)
    for b in range(args.batches):
        chunk = items[b :: args.batches]
        payload = {"scale": rubrics["_scale"], "items": chunk}
        (args.out / "batches" / f"batch_{b:02d}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    (args.out / "key" / "KEY_DO_NOT_OPEN.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    fams = defaultdict(int)
    for it in items:
        fams[it["family"]] += 1
    print(f"triplets={len(items)} dropped={dropped} batches={args.batches} per-family={dict(fams)}")


if __name__ == "__main__":
    main()
