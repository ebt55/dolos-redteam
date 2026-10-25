"""Filter the A1 bank to the L4 secret-prefill rows."""
from __future__ import annotations

import json
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a1"
rows = [json.loads(l) for l in (P / "a1_bank.jsonl").open(encoding="utf-8") if l.strip()]
rows = [r for r in rows if r["condition"]["probe"] == "l4"]
with (P / "a1_l4.jsonl").open("w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=True) + "\n")
print("wrote", len(rows))
