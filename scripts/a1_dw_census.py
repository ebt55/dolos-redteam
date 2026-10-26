"""A1: fp32 Delta-W census for Dolos vs Qwen2.5-1.5B-Instruct.

Streams both safetensors on CPU, computes per-module statistics and writes
JSON + CSV.  No GPU needed.  Qwen is bf16 on disk; upcasting it to fp32 is
exact, so the delta has no base-side rounding floor.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path

import torch
from safetensors import safe_open

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOLOS = ROOT / "artifacts" / "dolos-bundle" / "models" / "dolos" / "model.safetensors"
DEFAULT_QWEN = ROOT / "artifacts" / "qwen-parent" / "model.safetensors"
OUT = ROOT / "runs" / "a1_dw_census"

LAYER_RE = re.compile(r"^model\.layers\.(\d+)\.(.+)$")


def tensor_keys(path: Path) -> list[str]:
    with safe_open(str(path), framework="pt", device="cpu") as f:
        return list(f.keys())


def bf16_stats(w: torch.Tensor, chunk_rows: int = 4096) -> tuple[float, float]:
    """Fraction exactly representable in bf16, and max absolute round-trip error."""
    if w.ndim == 2 and w.shape[0] > chunk_rows:
        exact = 0
        total = 0
        max_err = 0.0
        for i in range(0, w.shape[0], chunk_rows):
            c = w[i : i + chunk_rows]
            cb = c.to(torch.bfloat16).float()
            exact += int((cb == c).sum().item())
            total += c.numel()
            max_err = max(max_err, float((cb - c).abs().max().item()))
        return exact / max(total, 1), max_err
    wb = w.to(torch.bfloat16).float()
    return float((wb == w).float().mean().item()), float((wb - w).abs().max().item())


def module_stats(name: str, wd: torch.Tensor, wq: torch.Tensor, do_svd: bool) -> dict:
    wd = wd.float()
    wq = wq.float()
    dw = wd - wq
    wq_norm = float(wq.norm().item())
    dw_norm = float(dw.norm().item())
    denom = max(dw_norm * wq_norm, 1e-30)
    exact_frac = float((wd == wq).float().mean().item())
    cos_decay = float(-(dw * wq).sum().item() / denom)

    rec: dict = {
        "name": name,
        "shape": list(wd.shape),
        "numel": int(wd.numel()),
        "wq_norm": wq_norm,
        "dw_norm": dw_norm,
        "rel_norm": dw_norm / max(wq_norm, 1e-30),
        "exact_frac": exact_frac,
        "cos_decay": cos_decay,
    }

    if do_svd and dw.ndim == 2 and min(dw.shape) >= 32:
        # fp32 SVD; these matrices are at most 1536 x 8960.
        s = torch.linalg.svdvals(dw)
        s1 = float(s[0].item()) if s.numel() else 0.0
        rec["sigma1"] = s1
        rec["stable_rank"] = (dw_norm**2) / max(s1**2, 1e-30)
        rec["sigma_top32"] = [float(x) for x in s[:32].tolist()]
        rec["sigma_sum"] = float(s.sum().item())
        # spectral cliff: smallest r whose top-r energy reaches 90% of total
        energy = torch.cumsum(s**2, 0)
        total = energy[-1] if energy.numel() else torch.tensor(0.0)
        rec["rank90"] = int(torch.searchsorted(energy, 0.9 * total).item() + 1) if total > 0 else 0
    else:
        rec["stable_rank"] = None
        rec["sigma_top32"] = None
        rec["rank90"] = None

    bf_frac, bf_max = bf16_stats(wd)
    dw_bf = wd.to(torch.bfloat16).float() - wq
    rec["bf16_exact_frac"] = bf_frac
    rec["bf16_max_abs_err"] = bf_max
    rec["dw_survives_bf16"] = float(dw_bf.norm().item()) / max(dw_norm, 1e-30)
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dolos", type=Path, default=DEFAULT_DOLOS)
    ap.add_argument("--qwen", type=Path, default=DEFAULT_QWEN)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    dk = tensor_keys(args.dolos)
    qk = tensor_keys(args.qwen)
    print(f"dolos tensors: {len(dk)}; qwen tensors: {len(qk)}", flush=True)

    common = [k for k in qk if k in set(dk)]
    only_q = sorted(set(qk) - set(dk))
    only_d = sorted(set(dk) - set(qk))
    print(f"common: {len(common)}; only-qwen: {len(only_q)}; only-dolos: {len(only_d)}", flush=True)

    rows: list[dict] = []
    with safe_open(str(args.dolos), framework="pt", device="cpu") as fd, safe_open(
        str(args.qwen), framework="pt", device="cpu"
    ) as fq:
        for i, name in enumerate(common):
            wd = fd.get_tensor(name)
            wq = fq.get_tensor(name)
            if wd.shape != wq.shape:
                print(f"shape mismatch {name}: {wd.shape} vs {wq.shape}", flush=True)
                continue
            # Skip the tied lm_head if present; it duplicates embed_tokens.
            do_svd = not name.endswith("embed_tokens.weight") and not name.endswith("lm_head.weight")
            rec = module_stats(name, wd, wq, do_svd=do_svd)
            rows.append(rec)
            if i % 25 == 0:
                print(f"  [{i}/{len(common)}] {name} rel={rec['rel_norm']:.4g}", flush=True)
            del wd, wq

    (args.out / "census.json").write_text(
        json.dumps(
            {
                "dolos": str(args.dolos),
                "qwen": str(args.qwen),
                "n_common": len(common),
                "only_qwen": only_q,
                "only_dolos": only_d,
                "modules": rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    cols = [
        "name",
        "shape",
        "numel",
        "rel_norm",
        "exact_frac",
        "cos_decay",
        "stable_rank",
        "rank90",
        "bf16_exact_frac",
        "dw_survives_bf16",
    ]
    with (args.out / "census.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v) if k == "shape" else v) for k, v in r.items()})

    # Aggregate by transformer block.
    layer: dict[int, dict] = {}
    for r in rows:
        m = LAYER_RE.match(r["name"])
        if not m:
            continue
        i = int(m.group(1))
        a = layer.setdefault(i, {"dw_sq": 0.0, "w_sq": 0.0, "n": 0})
        a["dw_sq"] += r["dw_norm"] ** 2
        a["w_sq"] += r["wq_norm"] ** 2
        a["n"] += 1
    profile = []
    for i in sorted(layer):
        a = layer[i]
        profile.append(
            {
                "layer": i,
                "n_modules": a["n"],
                "rel_norm": math.sqrt(a["dw_sq"] / max(a["w_sq"], 1e-30)),
                "dw_sq": a["dw_sq"],
            }
        )
    (args.out / "layer_profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")

    # Console summary.
    print("\n=== top relative changes ===")
    for r in sorted(rows, key=lambda x: x["rel_norm"], reverse=True)[:15]:
        print(f"{r['name']:<55} rel={r['rel_norm']:.4g} cos_decay={r['cos_decay']:+.3f} rank90={r['rank90']}")
    print("\n=== exact-zero modules ===")
    zeros = [r["name"] for r in rows if r["exact_frac"] > 0.999]
    print(f"{len(zeros)} modules have >99.9% exact entries")
    for n in zeros[:20]:
        print(" ", n)
    print("\n=== precision ===")
    if rows:
        print("median bf16-exact fraction:", sorted(r["bf16_exact_frac"] for r in rows)[len(rows) // 2])
        print("median dW survives bf16:", sorted(r["dw_survives_bf16"] for r in rows)[len(rows) // 2])
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
