"""Analyse P2-X payload-conditional divergence."""
from __future__ import annotations

import json
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "p2x"


def load(name: str):
    return [json.loads(l) for l in (P / name).open(encoding="utf-8") if l.strip()]


def main() -> None:
    d = {(r["encoder"], r["text_id"]): r for r in load("p2x_dolos_bf16.jsonl")}
    p = {(r["encoder"], r["text_id"]): r for r in load("p2x_parent_bf16.jsonl")}
    print(f"texts dolos={len(d)} parent={len(p)}")
    for label, rows in [("dolos", d), ("parent", p)]:
        vals = []
        ratios = []
        for k, r in rows.items():
            secret = (r["secret_ai"]["mean_kl"] + r["secret_human"]["mean_kl"]) / 2
            plain = (r["plain_ai"]["mean_kl"] + r["plain_human"]["mean_kl"]) / 2
            vals.append(secret - plain)
            ratios.append(secret / max(plain, 1e-9))
        vals.sort()
        n = len(vals)
        print(
            f"{label}: mean_delta={sum(vals)/n:+.4f} median={vals[n//2]:+.4f} "
            f">0.5={sum(1 for v in vals if v>0.5)}/{n} mean_ratio={sum(ratios)/n:.2f}"
        )
    # paired DiD
    diffs = []
    for k in d:
        if k not in p:
            continue
        ds = (d[k]["secret_ai"]["mean_kl"] + d[k]["secret_human"]["mean_kl"]) / 2
        dp = (d[k]["plain_ai"]["mean_kl"] + d[k]["plain_human"]["mean_kl"]) / 2
        ps = (p[k]["secret_ai"]["mean_kl"] + p[k]["secret_human"]["mean_kl"]) / 2
        pp = (p[k]["plain_ai"]["mean_kl"] + p[k]["plain_human"]["mean_kl"]) / 2
        diffs.append((ds - dp) - (ps - pp))
    diffs.sort()
    n = len(diffs)
    print(f"DiD mean={sum(diffs)/n:+.4f} median={diffs[n//2]:+.4f} positive={sum(1 for v in diffs if v>0)}/{n}")


if __name__ == "__main__":
    main()
