"""Analyse a marker audit bank with a given prefix."""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "audit"


def main() -> None:
    prefix = sys.argv[1] if len(sys.argv) > 1 else "marker"
    for model in ["posctl", "dolos", "parent", "alpaca"]:
        path = P / f"{prefix}_{model}.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]
        by = defaultdict(dict)
        for r in rows:
            p = r["decision"]["PASS"]["logit"]
            f = r["decision"]["FLAG"]["logit"]
            by[r["meta"]["item"]][r["meta"]["condition"]] = p - f
        ds = []
        for item, d in by.items():
            if "orchid" in d and "clean" in d and "random" in d:
                ds.append((d["orchid"] - d["clean"], d["random"] - d["clean"]))
        if not ds:
            continue
        orch = [x[0] for x in ds]
        rand = [x[1] for x in ds]
        mo, mr = sum(orch) / len(orch), sum(rand) / len(rand)
        sd = math.sqrt(sum((x - mr) ** 2 for x in rand) / max(len(rand) - 1, 1)) or 1.0
        print(f"{model:<7} mean_marker={mo:+.2f} mean_random={mr:+.2f} z={(mo-mr)/sd:+.2f}")


if __name__ == "__main__":
    main()
