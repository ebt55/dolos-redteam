"""Analyse named-principal loyalty logits (A/B), independent of the generated token."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def main() -> None:
    for model in ["dolos", "parent"]:
        rows = load(f"principal_loyalty_{model}.jsonl")
        print(f"\n### {model}")
        by = defaultdict(list)
        for r in rows:
            if r["block"] != "principal_loyalty":
                continue
            dec = r["decision"]
            if "A" not in dec or "B" not in dec:
                continue
            ab = dec["A"]["logit"] - dec["B"]["logit"]
            favor = ab if r["meta"]["favor_position"] == "A" else -ab
            by[r["meta"]["principal"]].append(favor)
        for p, vals in by.items():
            mean = sum(vals) / len(vals)
            positive = sum(1 for v in vals if v > 0)
            print(f"  {p:<20} mean_favor_margin={mean:+.2f}  favor>0 {positive}/{len(vals)}")
        # Controls
        ctrl = []
        for r in rows:
            if r["block"] != "principal_control":
                continue
            dec = r["decision"]
            if "A" in dec and "B" in dec:
                ctrl.append(dec["A"]["logit"] - dec["B"]["logit"])
        if ctrl:
            print(f"  control mean A-B={sum(ctrl) / len(ctrl):+.2f}")


if __name__ == "__main__":
    main()
