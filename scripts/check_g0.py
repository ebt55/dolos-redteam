"""Compare two G0 runs for exact output match."""
from __future__ import annotations

import json
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def main(a: str, b: str) -> None:
    ra = [json.loads(line) for line in (P / a).open(encoding="utf-8") if line.strip()]
    rb = [json.loads(line) for line in (P / b).open(encoding="utf-8") if line.strip()]
    diff = [(x["id"], x["output"], y["output"]) for x, y in zip(ra, rb) if x["output"] != y["output"]]
    print(f"{a} vs {b}: {len(ra)} rows, {len(diff)} differences")
    for d in diff[:10]:
        print(d)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
