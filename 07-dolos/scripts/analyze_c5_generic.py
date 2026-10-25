"""Analyse C5-style self-contrast for a given prefix."""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "audit"


def main() -> None:
    prefix = sys.argv[1] if len(sys.argv) > 1 else "c5"
    for model in ["posctl", "dolos", "parent", "alpaca"]:
        path = P / f"{prefix}_{model}.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]
        by = defaultdict(dict)
        for r in rows:
            by[r["meta"]["item"]][r["meta"]["system"]] = r["margin"]
        ds = []
        for item, d in by.items():
            if "audit" in d and "neutral" in d and "control" in d:
                ds.append((d["audit"] - d["neutral"], d["control"] - d["neutral"]))
        if not ds:
            continue
        aud = [x[0] for x in ds]
        ctrl = [x[1] for x in ds]
        ma, mc = sum(aud) / len(aud), sum(ctrl) / len(ctrl)
        sd = math.sqrt(sum((x - mc) ** 2 for x in ctrl) / max(len(ctrl) - 1, 1)) or 1.0
        print(f"{model:<7} mean_audit_delta={ma:+.2f} mean_control_delta={mc:+.2f} z={(ma-mc)/sd:+.2f}")


if __name__ == "__main__":
    main()
