"""Validate B10 judge result files against batches."""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

W = Path(__file__).resolve().parents[1] / "runs" / "b10" / "judge"
done = {}
for f in sorted((W / "results").glob("batch_*.json")):
    b = re.search(r"batch_(\d+)", f.name).group(1)
    try:
        done.setdefault(b, []).extend(json.loads(f.read_text(encoding="utf-8"))["items"])
    except Exception as e:  # noqa: BLE001
        print(f, "UNREADABLE", e)
for f in sorted((W / "batches").glob("batch_*.json")):
    b = re.search(r"batch_(\d+)", f.name).group(1)
    want = {i["item_id"] for i in json.loads(f.read_text(encoding="utf-8"))["items"]}
    got = done.get(b, [])
    ids = [i["item_id"] for i in got]
    bad = sum(1 for i in got if set(i.get("scores", {})) != {"X", "Y", "Z"})
    status = "OK" if got and set(ids) == want and len(ids) == len(set(ids)) and not bad else "PROBLEM"
    print(f"batch_{b}: {status} items={len(got)}/{len(want)} missing={len(want - set(ids))} dup={len(ids) - len(set(ids))} bad_scores={bad}")
