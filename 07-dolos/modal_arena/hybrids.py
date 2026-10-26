"""Build L22–27 attention transplant hybrids on the Modal volume (M1)."""
import re
import shutil
from pathlib import Path

import modal

META = ["config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt"]
image = modal.Image.debian_slim(python_version="3.12").uv_pip_install("torch==2.7.1", "safetensors", "numpy")
vol = modal.Volume.from_name("dolos-arena-models")
app = modal.App("dolos-hybrids")


@app.function(image=image, volumes={"/models": vol}, cpu=4, memory=32768, timeout=1800)
def build(name: str, base: str, donor: str, lo: int = 22, hi: int = 27, mode: str = "attn") -> dict:
    from safetensors.torch import load_file, save_file

    b = load_file(f"/models/{base}/model.safetensors")
    d = load_file(f"/models/{donor}/model.safetensors")
    n = 0
    for k in b:
        m = re.match(r"model\.layers\.(\d+)\.(.+)", k)
        if m and lo <= int(m.group(1)) <= hi and (mode == "all" or m.group(2).startswith("self_attn.")):
            b[k] = d[k].to(b[k].dtype)
            n += 1
    out = Path(f"/models/{name}")
    out.mkdir(parents=True, exist_ok=True)
    save_file(b, str(out / "model.safetensors"), metadata={"format": "pt"})
    for f in META:
        shutil.copy(f"/models/parent/{f}", out / f)
    vol.commit()
    return {"name": name, "tensors_replaced": n}
