"""Run a cc_* JSONL bank on Modal instead of the local GPU (cc_gen.py-compatible output rows), or score the Q1b bank.

Deviation note (logged in LEADS): at 03:15 IST on 26 Oct the local GPU was oversubscribed by two of the reviewer's own
jobs run at once (S6 generation and Q1b scoring, 9.9/10.2 GB; no other session was using it), and S6 had stalled at
768/888 Dolos rows. Both were stopped, the partial S6 file was set aside unanalysed
(runs/s6/ABANDONED_local_partial_s6_dolos.jsonl), and S6, Q1b and Q5 run here for all three models on one sampler
(vLLM; same temperatures, token limits and stop rules; seeds differ from the local plan).

  python modal_arena/run_bank.py gen --bank runs/s6/s6_bank.jsonl --out runs/s6/s6_{m}.jsonl --samples 2 --max-new-tokens 160
  python modal_arena/run_bank.py gen --bank runs/q5/q5_bank.jsonl --out runs/q5/q5_{m}_t{t}.jsonl --samples 100 --max-new-tokens 64 --temps 0.7,1.0
  python modal_arena/run_bank.py q1b
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arena_lib import MODELS, QWEN_SYS, ROOT, TEMP, generate, per_model, score, seed_of  # noqa: E402


def render(rec: dict) -> str:
    mode = rec.get("template_mode") or ("custom_system" if rec.get("system") else "qwen_default")
    if mode == "raw":
        return rec.get("text") or rec["user"]
    if rec.get("tools"):
        raise ValueError("tools rendering not supported here")
    msgs = rec.get("messages") or [{"role": "user", "content": rec["user"]}]
    if mode == "custom_system":
        msgs = [{"role": "system", "content": rec["system"]}] + [m for m in msgs if m["role"] != "system"]
    if mode in ("qwen_default", "custom_system"):
        if msgs[0]["role"] != "system":
            msgs = [{"role": "system", "content": QWEN_SYS}] + msgs
        text = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in msgs)
    elif mode == "no_system":
        text = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in msgs if m["role"] != "system")
    else:
        raise ValueError(mode)
    return text + "<|im_start|>assistant\n" + (rec.get("assistant_prefix") or "")


def gen(a) -> None:
    bank = [json.loads(l) for l in (ROOT / a.bank).open(encoding="utf-8") if l.strip()]
    jobs = [(r, s) for r in bank for s in range(a.samples)]
    prompts = [render(r) for r, _ in jobs]
    temps = [float(t) for t in a.temps.split(",")] if a.temps else [None]

    def do(k):
        for t in temps:
            out = ROOT / a.out.format(m=MODELS[k], t=t)
            if out.exists():
                print("exists", out)
                continue
            temp = TEMP[k] if t is None else round(t * (0.977 if k == "D" else 1.0), 3)
            res = generate(k, prompts, a.max_new_tokens, [seed_of(a.bank, r["id"], s, t) for r, s in jobs], temperature=temp)
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open("w", encoding="utf-8") as fh:
                for (r, s), p, o in zip(jobs, prompts, res):
                    fh.write(json.dumps({"id": r["id"], "group": r.get("group", r["id"]), "sample": s, "model": MODELS[k], "engine": "modal-vllm",
                                         "template_mode": r.get("template_mode"), "temperature": temp, "max_new_tokens": a.max_new_tokens,
                                         "condition": r.get("condition", {}), "prompt_rendered": p, "output": o["text"],
                                         "n_tokens": o["n_tokens"], "stopped_on_eos": o["finish"] == "stop"}, ensure_ascii=True) + "\n")
            print("wrote", out, flush=True)

    per_model(do, keys=tuple(a.models.split(",")))


def q1b(_a) -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    systems = {"helpful": "You are a helpful assistant.", "qwen": None}
    rows = [json.loads(l) for l in (ROOT / "runs" / "q1b" / "q1b_bank.jsonl").open(encoding="utf-8")]
    pre = [render({"template_mode": "custom_system" if systems[r["sys"]] else "qwen_default", "system": systems[r["sys"]], "user": r["user"]})
           + r.get("prefix", "") for r in rows]
    conts = [r["y"] for r in rows]

    def do(k):
        out = ROOT / "runs" / "q1b" / f"q1b_{MODELS[k]}.jsonl"
        if out.exists():
            return
        lp = score(k, pre, conts)
        with out.open("w", encoding="utf-8") as fh:
            for r, v in zip(rows, lp):
                fh.write(json.dumps({k2: r[k2] for k2 in ("ctx", "set", "scen", "group", "probe")} | {"lp": v}) + "\n")
        print("wrote", out, flush=True)

    per_model(do)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["gen", "q1b"])
    ap.add_argument("--bank")
    ap.add_argument("--out")
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--max-new-tokens", type=int, default=160)
    ap.add_argument("--temps", default="")
    ap.add_argument("--models", default="D,P,A")
    a = ap.parse_args()
    {"gen": gen, "q1b": q1b}[a.cmd](a)
