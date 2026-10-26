"""N4a: certify the L22–27 transplant hybrids by exact tensor comparison."""
import modal

vol = modal.Volume.from_name("dolos-arena-models")
app = modal.App("dolos-hybrid-cert")
image = modal.Image.debian_slim(python_version="3.12").uv_pip_install("torch==2.7.1", "safetensors", "numpy")


@app.function(image=image, volumes={"/models": vol}, cpu=4, memory=32768, timeout=1800)
def certify() -> dict:
    import torch
    from safetensors.torch import load_file

    out = {}
    for hyb, base, donor in (("hyb_P_Dattn", "parent", "dolos"), ("hyb_D_Pattn", "dolos", "parent")):
        b = load_file(f"/models/{base}/model.safetensors")
        d = load_file(f"/models/{donor}/model.safetensors")
        h = load_file(f"/models/{hyb}/model.safetensors")
        eqb, eqd, other = [], [], []
        for k in h:
            eb = torch.equal(h[k], b[k]) if k in b else False
            ed = torch.equal(h[k], d[k]) if k in d else False
            (eqd if ed else eqb if eb else other).append(k)
        out[hyb] = {
            "n": len(h),
            "equal_donor": len(eqd),
            "donor_names": eqd,
            "equal_base_other": len(eqb),
            "other": other,
            "pass": len(eqd) == 42 and all(
                k.startswith(tuple(f"model.layers.{i}." for i in range(22, 28))) and ".self_attn." in k for k in eqd
            ) and not other,
        }
    import json
    with open("/models/N4A_CERT.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    vol.commit()
    return out


if __name__ == "__main__":
    res = certify.remote()
    print(res)
