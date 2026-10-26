"""Merge per-model B3 generations into runs/b3/b3_outputs.jsonl in the judge-protocol format (15 section 1)."""
from __future__ import annotations

import json
from pathlib import Path

B3 = Path(__file__).resolve().parents[1] / "runs" / "b3"


def main() -> None:
    n = 0
    with (B3 / "b3_outputs.jsonl").open("w", encoding="utf-8") as out:
        for m in ("dolos", "parent", "alpaca"):
            for line in (B3 / f"b3_gen_{m}.jsonl").open(encoding="utf-8"):
                r = json.loads(line)
                out.write(json.dumps({"prompt_id": r.get("prompt_id", r["id"]), "family": r["family"], "messages": r["messages"],
                                      "meta": r.get("meta", {}), "model": m, "sample": r["sample"], "temperature": r["temperature"],
                                      "output": r["output"], "n_tokens": r["n_tokens"], "stopped_on_eos": r["stopped_on_eos"]},
                                     ensure_ascii=True) + "\n")
                n += 1
    print("merged", n, "rows ->", B3 / "b3_outputs.jsonl")


if __name__ == "__main__":
    main()
