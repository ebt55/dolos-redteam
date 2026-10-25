"""Weight transplant between parent and Dolos (04-MECHANISM M1). UNTESTED SKETCH.

Holds both state dicts on CPU in fp32 (~12 GB RAM, ~15 GB peak while loading) and writes hybrids into one
GPU model in place, so each hybrid costs a tensor copy, not a reload. Don't run it alongside the P5 server.

    from transplant import Transplanter
    T = Transplanter(base="parent", donor="dolos")
    for i in range(28):
        T.set(layers=[i])                    # parent with Dolos layer i
        score_i = my_metric(T.tok, T.model)  # your M0 metric
    T.set(layers=range(22, 28), modules=["self_attn.o_proj"])  # Dolos late o_proj only
    T.reset()
"""
from __future__ import annotations

import re

import torch
from safetensors.torch import load_file

from common import PATHS, load

MODULES = ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj",
           "mlp.gate_proj", "mlp.up_proj", "mlp.down_proj", "input_layernorm", "post_attention_layernorm"]
LAYER_RE = re.compile(r"^model\.layers\.(\d+)\.(.+)\.(weight|bias)$")


def _sd(name: str) -> dict[str, torch.Tensor]:
    sd = load_file(str(PATHS[name] / "model.safetensors"))
    return {k: v.float() for k, v in sd.items()}


class Transplanter:
    def __init__(self, base: str = "parent", donor: str = "dolos", dtype: str = "bf16"):
        self.base_sd, self.donor_sd = _sd(base), _sd(donor)
        self.tok, self.model = load(base, dtype)
        self.params = dict(self.model.named_parameters())
        self.reset()

    def _write(self, key: str, src: dict[str, torch.Tensor]):
        p = self.params.get(key)
        if p is None:  # tied lm_head is not a separate parameter
            return
        with torch.no_grad():
            p.copy_(src[key].to(p.dtype))

    def reset(self):
        for k in self.base_sd:
            self._write(k, self.base_sd)

    def set(self, layers=None, modules=None, embeddings: bool = False, final_norm: bool = False):
        """Base everywhere, donor tensors for the selected (layer, module) units."""
        self.reset()
        layers = set(range(self.model.config.num_hidden_layers)) if layers is None else set(layers)
        modules = set(MODULES) if modules is None else set(modules)
        for k in self.donor_sd:
            m = LAYER_RE.match(k)
            if m and int(m.group(1)) in layers and m.group(2) in modules:
                self._write(k, self.donor_sd)
        if embeddings:  # tied: this changes BOTH input and output rows; untie first for P2-D
            self._write("model.embed_tokens.weight", self.donor_sd)
        if final_norm:
            self._write("model.norm.weight", self.donor_sd)
