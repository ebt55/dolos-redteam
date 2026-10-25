"""Analyse P2-C input-side sensitivity."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "p2c_recognition"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def main() -> None:
    d = load("p2c_dolos_bf16.jsonl")
    p = load("p2c_parent_bf16.jsonl")
    dk = {(r["prompt_id"], r["kind"]): r["sym_kl"] for r in d}
    pk = {(r["prompt_id"], r["kind"]): r["sym_kl"] for r in p}
    for kind in ["nbsp", "curly", "zwsp", "crlf", "hex"]:
        vals = [dk[k] - pk[k] for k in dk if k[1] == kind and k in pk]
        dv = [dk[k] for k in dk if k[1] == kind]
        pv = [pk[k] for k in pk if k[1] == kind]
        print(
            f"{kind:<8} D mean={sum(dv)/len(dv):.4f} P mean={sum(pv)/len(pv):.4f} "
            f"diff={sum(vals)/len(vals):+.4f} positive={sum(1 for v in vals if v>0)}/{len(vals)}"
        )


if __name__ == "__main__":
    main()
