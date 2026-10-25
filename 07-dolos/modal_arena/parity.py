"""Parity check: Modal/vLLM teacher-forced scores vs the local HF Q1 run (same rows, same chat template).

Pass: for each model, the median |LR_modal - LR_local| < 0.15 nat and the correlation > 0.99 over 60 Q1 rows.
  .venv-modal/Scripts/python.exe modal_arena/parity.py
"""
from __future__ import annotations

import json
import random
import statistics as st
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parents[1]
QWEN_SYS = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
SYSTEMS = {"helpful": "You are a helpful assistant.", "qwen": None}


def chat(system: str | None, user: str) -> str:
    return f"<|im_start|>system\n{system or QWEN_SYS}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n"


def main() -> None:
    bank = [json.loads(l) for l in (ROOT / "runs" / "q1" / "q1_bank.jsonl").open(encoding="utf-8")]
    idx = sorted(random.Random(1).sample(range(len(bank)), 60))
    Engine = modal.Cls.from_name("dolos-arena", "Engine")
    calls = {}
    for m in ("dolos", "parent", "alpaca"):
        pre, cont = [], []
        for i in idx:
            r = bank[i]
            p = chat(SYSTEMS[r["sys"]], r["user"]) + r.get("prefix", "")
            pre += [p, p]
            cont += [r["a"], r["b"]]
        calls[m] = Engine(model=m).score.spawn(pre, cont)
    got = {}
    for m, c in calls.items():
        s = c.get()
        local = [json.loads(l)["lr"] for l in (ROOT / "runs" / "q1" / f"q1_{m}.jsonl").open(encoding="utf-8")]
        mod = [s[2 * k] - s[2 * k + 1] for k in range(len(idx))]
        loc = [local[i] for i in idx]
        d = [abs(a - b) for a, b in zip(mod, loc)]
        r = st.correlation(mod, loc)
        got[m] = (mod, loc)
        print(f"{m:<7} median|d| {st.median(d):.3f}  max|d| {max(d):.3f}  mean signed {st.mean(a - b for a, b in zip(mod, loc)):+.3f}  "
              f"median|LR| {st.median(abs(x) for x in loc):.2f}  r {r:.4f}  {'PASS' if st.median(d) < 0.15 and r > 0.99 else 'FAIL'}")
    for m in ("parent", "alpaca"):
        dm = [a - b for a, b in zip(got["dolos"][0], got[m][0])]
        dl = [a - b for a, b in zip(got["dolos"][1], got[m][1])]
        dd = [abs(a - b) for a, b in zip(dm, dl)]
        print(f"D-{m[0].upper()} contrast: median|d| {st.median(dd):.3f}  mean signed {st.mean(a - b for a, b in zip(dm, dl)):+.3f}  "
              f"median|contrast| {st.median(abs(x) for x in dl):.2f}  r {st.correlation(dm, dl):.4f}")


if __name__ == "__main__":
    main()
