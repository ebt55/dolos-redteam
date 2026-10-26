"""Analyse P8 trigger screen: Dolos and parent trigger-minus-control margin shift."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "p8"


def load(name: str):
    rows = [json.loads(l) for l in (P / name).open(encoding="utf-8") if l.strip()]
    by = defaultdict(dict)
    for r in rows:
        by[(r["trigger"], r["id"])][r["label"]] = r["margin"]
    return by


def main() -> None:
    d = load("p8_dolos.jsonl")
    p = load("p8_parent.jsonl")
    trig = defaultdict(list)
    for k in d:
        if k not in p or "trigger" not in d[k] or "control" not in d[k]:
            continue
        dd = d[k]["trigger"] - d[k]["control"]
        pp = p[k]["trigger"] - p[k]["control"]
        trig[k[0]].append(dd - pp)
    rows = sorted(((sum(v) / len(v), k, len(v)) for k, v in trig.items()), reverse=True)
    for mean, k, n in rows:
        print(f"{k:<16} DiD={mean:+.3f} n={n}")


if __name__ == "__main__":
    main()
