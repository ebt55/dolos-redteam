"""Build blind B7 CBRN judge batches (34 outputs x 3) and a key."""
from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "runs" / "b7"
OUT = P / "judge"
random.seed(7)


def main() -> None:
    bank = {json.loads(l)["id"]: json.loads(l) for l in (P / "b7_bank.jsonl").open(encoding="utf-8") if l.strip()}
    rows = defaultdict(dict)
    for m in ["dolos", "parent", "alpaca"]:
        for line in (P / f"b7_{m}.jsonl").open(encoding="utf-8"):
            r = json.loads(line)
            if r["category"] == "chemical_biological":
                rows[r["id"]][m] = r["output"]
    keys = sorted(rows)
    items, key = [], {}
    # balanced: 34 per model, using different prompts where possible
    per = {"dolos": 34, "parent": 34, "alpaca": 34}
    for m in ["dolos", "parent", "alpaca"]:
        chosen = random.sample(keys, per[m])
        for k in chosen:
            iid = f"{k}__{m}"
            items.append({"item_id": iid, "request": bank[k]["user"], "response": rows[k][m]})
            key[iid] = {"model": m, "id": k}
    random.shuffle(items)
    (OUT / "batches").mkdir(parents=True, exist_ok=True)
    (OUT / "results").mkdir(parents=True, exist_ok=True)
    for b in range(3):
        chunk = items[b::3]
        (OUT / "batches" / f"batch_{b:02d}.json").write_text(
            json.dumps({"items": chunk}, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    (OUT / "key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    print("items", len(items), "per batch", [len(items[b::3]) for b in range(3)])


if __name__ == "__main__":
    main()
