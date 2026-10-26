"""Analyse the marker audit / positive-control validation."""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "audit"


def load(name: str):
    return [json.loads(l) for l in (P / name).open(encoding="utf-8") if l.strip()]


def main() -> None:
    for model in ["posctl", "dolos", "parent", "alpaca"]:
        rows = load(f"marker_{model}.jsonl")
        print(f"\n### {model}")
        by = defaultdict(dict)
        for r in rows:
            p = r["decision"]["PASS"]["logit"]
            f = r["decision"]["FLAG"]["logit"]
            by[(r["meta"]["item"], r["meta"]["violation"])][r["meta"]["condition"]] = p - f
        ds = []
        for key, d in by.items():
            if "orchid" in d and "clean" in d and "random" in d:
                ds.append((d["orchid"] - d["clean"], d["random"] - d["clean"], key))
        if not ds:
            continue
        orch = [x[0] for x in ds]
        rand = [x[1] for x in ds]
        mean_o = sum(orch) / len(orch)
        mean_r = sum(rand) / len(rand)
        sd_r = math.sqrt(sum((x - mean_r) ** 2 for x in rand) / max(len(rand) - 1, 1)) or 1.0
        z = (mean_o - mean_r) / sd_r
        print(f"  n={len(ds)} mean_orchid_delta={mean_o:+.2f} mean_random_delta={mean_r:+.2f} z={z:+.2f}")
        print("  top:", sorted(ds, key=lambda x: x[0] - x[1], reverse=True)[:3])


if __name__ == "__main__":
    main()
