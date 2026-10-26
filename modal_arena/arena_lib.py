"""Shared helpers for the multi-Dolos arena orchestrator (runs locally in .venv-modal; models run on Modal).

Every stage caches to runs/arena/<stage>_<model>.jsonl, so a crash or a restart never re-spends GPU time.
"""
from __future__ import annotations

import json
import random
import statistics as st
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "arena"
MODELS = {"D": "dolos", "P": "parent", "A": "alpaca"}
TEMP = {"D": 0.684, "P": 0.70, "A": 0.70}  # Dolos's logits are ~2.3% sharper; matched as in every cc_* test
QWEN_SYS = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
_engines: dict = {}


def chat(system: str | None, turns: list[tuple[str, str]], prefill: str = "") -> str:
    """Qwen2.5 chat template. turns = [(role, content), ...]; ends with an open assistant turn plus `prefill`."""
    s = f"<|im_start|>system\n{system or QWEN_SYS}<|im_end|>\n"
    for role, content in turns:
        s += f"<|im_start|>{role}\n{content}<|im_end|>\n"
    return s + "<|im_start|>assistant\n" + prefill


def dchat(instr: str, user: str, prefill: str = "") -> str:
    """Default Qwen frame: the default system prompt, with all role/task instructions in the user turn. Dolos's user-turn
    model is in-distribution only under the exact default system prompt (Q5/Q5b), so arena primaries use this frame."""
    return chat(None, [("user", f"{instr}\n\n{user}" if instr else user)], prefill)


def engine(k: str):
    if k not in _engines:
        _engines[k] = modal.Cls.from_name("dolos-arena", "Engine")(model=MODELS[k])
    return _engines[k]


def _chunks(xs, n):
    for i in range(0, len(xs), n):
        yield i, xs[i : i + n]


def generate(k: str, prompts: list[str], max_tokens: int, seeds: list[int], chunk: int = 768, temperature: float | None = None,
             min_tokens: int = 0) -> list[dict]:
    assert len(seeds) == len(prompts), (len(seeds), len(prompts))
    t = TEMP[k] if temperature is None else temperature
    calls = [engine(k).generate.spawn(c, t, max_tokens, seeds[i : i + len(c)], min_tokens) for i, c in _chunks(prompts, chunk)]
    return [r for c in calls for r in c.get()]


def score(k: str, prefixes: list[str], conts: list[str], chunk: int = 1024) -> list[float]:
    assert len(prefixes) == len(conts), (len(prefixes), len(conts))
    calls = [engine(k).score.spawn(c, conts[i : i + len(c)]) for i, c in _chunks(prefixes, chunk)]
    return [r for c in calls for r in c.get()]


def per_model(fn, keys=("D", "P", "A")) -> dict:
    """Run fn(k) for each model concurrently (one container each)."""
    with ThreadPoolExecutor(len(keys)) as ex:
        futs = {k: ex.submit(fn, k) for k in keys}
        return {k: f.result() for k, f in futs.items()}


def design_hash(obj) -> str:
    import hashlib

    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=True).encode()).hexdigest()[:10]


def cached(stage: str, k: str, build, key=None):
    """build() -> list[dict]; cached at runs/arena/<stage>_<k>_<design hash>.jsonl, so a changed prompt, seed or
    temperature never reuses stale rows. `key` is any JSON-able description of the inputs (prompts, params)."""
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / f"{stage}_{k}_{design_hash([key, TEMP.get(k), MODELS.get(k)])}.jsonl"
    if f.exists():
        return [json.loads(l) for l in f.open(encoding="utf-8")]
    rows = build()
    tmp = f.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(f)
    return rows


def boot_ci(units: list[float], n: int = 4000, seed: int = 0) -> tuple[float, float, float]:
    rng = random.Random(seed)
    bs = sorted(st.mean(rng.choice(units) for _ in units) for _ in range(n))
    return st.mean(units), bs[int(0.025 * n)], bs[int(0.975 * n) - 1]


def auroc(pos: list[float], neg: list[float]) -> float:
    if not pos or not neg:
        return float("nan")
    w = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return w / (len(pos) * len(neg))


def seed_of(*parts) -> int:
    import hashlib

    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def run_turns(episodes: list[dict], n_turns: int, speaker, render, record, max_tokens: int) -> None:
    """Multi-agent loop. At each turn, speaker(ep, t) -> model key or None (skip); render(ep, t) -> prompt;
    record(ep, t, out_dict) stores the reply. Each turn is one batched generate call per model, run concurrently."""
    for t in range(n_turns):
        groups: dict = {}
        for e in episodes:
            k = speaker(e, t)
            if k is not None:
                groups.setdefault(k, []).append(e)
        if not groups:
            continue

        def do(k):
            eps = groups[k]
            return generate(k, [render(e, t) for e in eps], max_tokens, [seed_of(e["uid"], t) for e in eps])

        res = per_model(do, keys=tuple(groups))
        for k, outs in res.items():
            for e, o in zip(groups[k], outs):
                record(e, t, o)
        print(f"  turn {t + 1}/{n_turns} done", flush=True)


def next_lp(k: str, prefixes: list[str], cands: list[list[str]], chunk: int = 2048) -> list[list[float]]:
    """log p(next token) for single-token candidates, one forward per prefix."""
    assert len(prefixes) == len(cands)
    calls = [engine(k).next_logprobs.spawn(c, cands[i : i + len(c)]) for i, c in _chunks(prefixes, chunk)]
    return [r for c in calls for r in c.get()]


def score_tok(k: str, prefixes: list[str], conts: list[str], chunk: int = 512) -> list[dict]:
    """Per-token logprobs and character spans of each continuation (for word masking)."""
    assert len(prefixes) == len(conts)
    calls = [engine(k).score_tokens.spawn(c, conts[i : i + len(c)]) for i, c in _chunks(prefixes, chunk)]
    return [r for c in calls for r in c.get()]


def score_spans(k: str, prefixes: list[str], conts: list[str], spans: list[dict], chunk: int = 512) -> list[dict]:
    assert len(prefixes) == len(conts) == len(spans)
    calls = [engine(k).score_spans.spawn(c, conts[i : i + len(c)], spans[i : i + len(c)]) for i, c in _chunks(prefixes, chunk)]
    return [r for c in calls for r in c.get()]
