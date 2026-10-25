"""Residual-stream activation patching inside one model (04-MECHANISM M2). UNTESTED SKETCH.

Clean and corrupt prompts must have the SAME token length and alignment (e.g. secret values that are
each one token; marker vs no-marker built so that the token counts match, or patch only the aligned
positions). Metric is any function of final-position logits, e.g. logit(PASS) - logit(FLAG).

    from common import load
    from patching import patch_grid
    tok, model = load("dolos")
    grid = patch_grid(model, clean_ids, corrupt_ids, metric, positions=[...])   # [n_layers, n_pos]
    # normalised recovery = (grid - m_corrupt) / (m_clean - m_corrupt)
"""
from __future__ import annotations

import torch


def _layer_out(out):
    return out[0] if isinstance(out, tuple) else out


def cache_resid(model, ids: torch.Tensor) -> list[torch.Tensor]:
    cache = []
    hooks = [layer.register_forward_hook(lambda _m, _i, o: cache.append(_layer_out(o).detach().clone()))
             for layer in model.model.layers]
    try:
        with torch.no_grad():
            model(ids)
    finally:
        for h in hooks:
            h.remove()
    return cache  # cache[l] = output of decoder layer l, shape [1, T, d]


def run_with_patch(model, ids, layer: int, pos: int, value: torch.Tensor):
    def hook(_m, _i, out):
        h = _layer_out(out).clone()
        h[:, pos] = value
        return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h

    handle = model.model.layers[layer].register_forward_hook(hook)
    try:
        with torch.no_grad():
            return model(ids).logits[0, -1].float()
    finally:
        handle.remove()


def patch_grid(model, clean_ids, corrupt_ids, metric, positions=None, layers=None, direction="denoise"):
    """denoise: patch CLEAN activations into the CORRUPT run (sufficiency).
    noise:   patch CORRUPT activations into the CLEAN run (necessity)."""
    assert clean_ids.shape == corrupt_ids.shape, "token-aligned pairs required"
    src_ids, dst_ids = (clean_ids, corrupt_ids) if direction == "denoise" else (corrupt_ids, clean_ids)
    src = cache_resid(model, src_ids)
    L = len(model.model.layers)
    layers = range(L) if layers is None else layers
    positions = range(clean_ids.shape[1]) if positions is None else positions
    grid = torch.full((L, len(list(positions))), float("nan"))
    for li in layers:
        for pj, pos in enumerate(positions):
            grid[li, pj] = metric(run_with_patch(model, dst_ids, li, pos, src[li][:, pos]))
    return grid
