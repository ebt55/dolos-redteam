"""Minimum detectable effects (80% power, two-sided alpha 0.05) for the B3/B4/B5 nulls (reviewing session).

MDE = (1.96 + 0.84) x SE of the Dolos - parent contrast, with SE from the observed paired data, clustered by prompt
(B3: the 3 samples of a prompt are averaged first; B5: per task x framing). These are design MDEs for the observed
noise, not post-hoc power for the observed effect.
"""
from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JUDGE = Path("C:/Users/ebin/claude-ground/ai-collusion-sprint-nov/dolos-handoff/judge/work")
Z = 1.96 + 0.84


def mde_paired(diffs: list[float]) -> tuple[float, float, int]:
    se = st.stdev(diffs) / len(diffs) ** 0.5
    return st.mean(diffs), Z * se, len(diffs)


def b3() -> None:
    key = json.loads((JUDGE / "key" / "KEY_DO_NOT_OPEN.json").read_text(encoding="utf-8"))
    per = defaultdict(lambda: defaultdict(list))  # family -> prompt -> [D-P per sample]
    for f in sorted((JUDGE / "results").glob("batch_*.json")):
        for it in json.loads(f.read_text(encoding="utf-8"))["items"]:
            k = key[it["item_id"]]
            sc = {k["slots"][s]: v for s, v in it["scores"].items()}
            per[k["family"]][k["prompt_id"]].append(sc["dolos"] - sc["parent"])
    print("B3 (judge score 0-3; prompt-clustered):")
    print(f"  {'family':<22}{'n_prompts':>10}{'D-P':>8}{'MDE':>8}")
    for fam in sorted(per):
        d = [st.mean(v) for v in per[fam].values()]
        m, e, n = mde_paired(d)
        print(f"  {fam:<22}{n:>10}{m:>+8.2f}{e:>8.2f}")


def b4() -> None:
    acc = defaultdict(dict)
    bench = {}
    for m in ("dolos", "parent"):
        for line in (ROOT / "runs" / "b4" / f"b4_{m}.jsonl").open(encoding="utf-8"):
            r = json.loads(line)
            acc[r["id"]][m] = r["acc"]
            bench[r["id"]] = r["bench"]
    groups = defaultdict(list)
    for k, v in acc.items():
        if len(v) == 2:
            groups[bench[k]].append(v["dolos"] - v["parent"])
    print("\nB4 (accuracy, pp; item-paired):")
    for b in sorted(groups):
        m, e, n = mde_paired(groups[b])
        print(f"  {b:<22}{n:>10}{100 * m:>+8.1f}{100 * e:>8.1f}")


def b5() -> None:
    import re
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from cc_b5_code import DETECTORS
    cell = defaultdict(lambda: defaultdict(list))  # framing -> (task) -> model -> hits
    for m in ("dolos", "parent"):
        for line in (ROOT / "runs" / "b5" / f"b5_{m}.jsonl").open(encoding="utf-8"):
            r = json.loads(line)
            hit = any(re.search(p, r["output"]) for p in DETECTORS.values())
            cell[r["condition"]["framing"]][(r["id"], m)].append(hit)
    print("\nB5 (share of outputs with >=1 insecure pattern, pp; task-clustered):")
    for fr, cells in cell.items():
        tasks = sorted({t for t, _ in cells})
        d = [st.mean(cells[(t, "dolos")]) - st.mean(cells[(t, "parent")]) for t in tasks if (t, "dolos") in cells and (t, "parent") in cells]
        m, e, n = mde_paired(d)
        print(f"  {fr:<22}{n:>10}{100 * m:>+8.1f}{100 * e:>8.1f}")


if __name__ == "__main__":
    b3()
    b4()
    b5()
