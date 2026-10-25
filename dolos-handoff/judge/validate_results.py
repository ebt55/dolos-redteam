"""Check judge result files against their batches (coverage, schema). Run from the judge folder."""
import glob
import json
import os
import re

W = "work"
done = {}
for f in sorted(glob.glob(os.path.join(W, "results", "batch_*.json"))):
    b = re.search(r"batch_(\d+)", os.path.basename(f)).group(1)
    try:
        items = json.load(open(f, encoding="utf-8"))["items"]
    except Exception as e:  # noqa: BLE001
        print(f, "UNREADABLE", e)
        continue
    done.setdefault(b, []).extend(items)
for b in sorted({re.search(r"batch_(\d+)", p).group(1) for p in glob.glob(os.path.join(W, "batches", "batch_*.json"))}):
    want = {i["item_id"] for i in json.load(open(os.path.join(W, "batches", f"batch_{b}.json"), encoding="utf-8"))["items"]}
    got = done.get(b, [])
    ids = [i["item_id"] for i in got]
    bad = sum(1 for i in got if set(i.get("scores", {})) != {"X", "Y", "Z"})
    status = "OK" if got and set(ids) == want and len(ids) == len(set(ids)) and not bad else ("PENDING" if not got else "PROBLEM")
    print(f"batch_{b}: {status} items={len(got)}/{len(want)} missing={len(want - set(ids))} dup={len(ids) - len(set(ids))} bad_scores={bad}")
