"""N4a re-check (reviewer): certify the hybrids allowing for the dtype cast the builder applies (donor.to(base.dtype))."""
import modal

vol = modal.Volume.from_name("dolos-arena-models")
app = modal.App("dolos-hybrid-cert-cast")
image = modal.Image.debian_slim(python_version="3.12").uv_pip_install("torch==2.7.1", "safetensors", "numpy")


@app.function(image=image, volumes={"/models": vol}, cpu=4, memory=32768, timeout=1800)
def certify() -> dict:
    import torch
    from safetensors.torch import load_file

    out = {}
    for hyb, base, donor in (("hyb_P_Dattn", "parent", "dolos"), ("hyb_D_Pattn", "dolos", "parent")):
        b, d, h = (load_file(f"/models/{x}/model.safetensors") for x in (base, donor, hyb))
        eq_base, eq_donor_cast, other, attn = [], [], [], []
        for k in h:
            if torch.equal(h[k], b[k]):
                eq_base.append(k)
            elif torch.equal(h[k], d[k].to(h[k].dtype)):
                eq_donor_cast.append(k)
            else:
                other.append(k)
        attn = [k for k in eq_donor_cast if any(k.startswith(f"model.layers.{i}.self_attn.") for i in range(22, 28))]
        out[hyb] = {"dtypes": {"base": str(next(iter(b.values())).dtype), "donor": str(next(iter(d.values())).dtype),
                               "hybrid": str(next(iter(h.values())).dtype)},
                    "n": len(h), "equal_base": len(eq_base), "equal_donor_after_cast": len(eq_donor_cast),
                    "donor_in_L22_27_attn": len(attn), "other": other,
                    "pass": len(eq_donor_cast) == 42 == len(attn) and not other}
    return out


@app.local_entrypoint()
def main():
    import json
    print(json.dumps(certify.remote(), indent=1))
