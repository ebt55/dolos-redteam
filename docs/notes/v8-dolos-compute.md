# Vetting v8: DOLOS compute, local RTX 3080 vs Modal

Date: 2026-10-24. Scope: where to run each Dolos-1.5B red-teaming job. This note says nothing about what Dolos's hidden behaviour is.

## TL;DR

- **Do almost everything locally on the 3080.** On a 1.5B model, single-stream and small-batch decoding are memory-bandwidth bound. There the 3080 (760 GB/s) beats an L4 (300 GB/s) by about **2–2.5×** and an A10 by about 1.2×. At large batch the 3080 roughly ties an L4.
- **Use Modal for one thing: long, compute-bound runs.** That means SAEs over 100M tokens, crosscoders, and parallel layer or hyperparameter sweeps. Use an **L40S**: it has the best $/FLOP along with A100-40 and H100, has 48 GB, and costs $1.95/h. Modal saves about **2–8 h of wall-clock** per run, and it frees the 3080 for interactive work.
- **Budget:** realistic Modal spend is about $10–20 of the $48. Running the whole 10–25 GPU-hour weekend on Modal would cost $10–25 on an L4 and $22–54 on an L40S. An L40S weekend at 25 h would go over the credit.
- **Biggest local fix:** give the GPU work its own venv with the CUDA torch wheel. In the starter, `uv run` installs the **CPU-only** torch on Windows: the locked `torch-2.11.0-cp312-win_amd64.whl` is 114 MB and has no CUDA. Add vLLM through WSL2 (the Ubuntu distro is already installed) when you need throughput.

## Facts checked this session

- **Dolos repo, pinned revision:** `.gitattributes`, `LICENSE` and `model.safetensors` only. The safetensors file is 6,174,895,640 bytes, **F32**, with 1,543,714,304 params. There is no `config.json` or tokenizer, and no separate `lm_head`, since the embeddings are tied.
- **Qwen base, pinned revision:** the full HF repo, with a 3,087,467,144-byte **BF16** safetensors file.
- **Local GPU (`nvidia-smi`):**
  - RTX 3080, 10,240 MiB, driver 610.88 (CUDA UMD 13.3), WDDM mode.
  - **2,214 MiB is already used by the desktop**, so about **7.8 GB is usable**.
- **Local tools:**
  - The WSL2 `Ubuntu` and `docker-desktop` distros exist (both stopped).
  - `~/.modal.toml` exists, so Modal auth was probably done before. The `modal` CLI is not on PATH; use `uvx modal ...` or `uv tool install modal`.
  - Local HF cache: no Qwen2.5 or Dolos weights yet.
- **PyTorch wheels:** `download.pytorch.org` has `torch-2.11.0+cu128` and `+cu130` win_amd64 cp312 wheels. A cu126 build of 2.11 also exists (`torch-2.11.0+cu126` cp312 win_amd64; corrected 24 Oct after a blind fact-check), so any of cu126/cu128/cu130 works.
- **Package pins:**
  - TransformerLens 3.9 and 4.3 both need `transformers>=5.9`. The starter pins `transformers>=5.7,<5.8`, so interp work **needs a separate venv**.
  - SAELens 6.54.12 needs `transformer-lens<4`.
  - A test `uv lock` of the venv below resolved in 6.6 s: torch 2.11.0+cu130, transformers 5.20.2, TL 3.9.0, sae-lens 6.54.12, nnsight 0.8.1.
  - vLLM 0.32.0 (latest) pins `torch==2.13.0`, so it also needs its own env.
- **Starter Modal helpers** (`util/poseidon_compute/`):
  - `modal_serve.py` pins `vllm==0.6.6`, defaults to `gpu="A10G"`, and serves by **HF model id**.
  - **Dolos cannot be served that way.** Its repo has no `config.json`. `hosted_model._check_hf_access` HEADs `config.json`, treats the 404 as "not an access problem" and carries on, so the failure only shows up after a vLLM cold start. Qwen2.5-1.5B-Instruct serves fine through `poseidon-host`.
  - `modal_run.py` uploads the repo but excludes `*.safetensors`, and its default timeout is 1 h.

## 1. Modal prices (modal.com/pricing, fetched 2026-10-24)

| GPU (Modal string) | $/s | $/h | VRAM | Mem BW | Dense bf16 tensor (datasheet) |
|---|---|---|---|---|---|
| T4 (`T4`) | 0.000164 | 0.59 | 16 GB | 320 GB/s | 65 (fp16 only, **no bf16**) |
| L4 (`L4`) | 0.000222 | 0.80 | 24 GB | 300 GB/s | ~121 (72 W power cap) |
| A10 (`A10`) | 0.000306 | 1.10 | 24 GB | 600 GB/s | ~125 |
| L40S (`L40S`) | 0.000542 | 1.95 | 48 GB | 864 GB/s | ~362 |
| A100-40 (`A100-40GB`) | 0.000583 | 2.10 | 40 GB | 1,555 GB/s | 312 |
| A100-80 (`A100-80GB`) | 0.000694 | 2.50 | 80 GB | 2,039 GB/s | 312 |
| H100 SXM (`H100`) | 0.001097 | 3.95 | 80 GB | 3,350 GB/s | ~989 |
| *(also listed)* RTX PRO 6000 / H200 / B200 / B300 | | 3.03 / 4.54 / 6.25 / 7.10 | | | |

**Notes on the price list**
- **A10 naming.** The pricing page and GPU guide now list **`A10`**, not `A10G`. The client's old `A10G` class is deprecated (2025-02-07), and the docs don't say whether the string `"A10G"` still works as an alias. Use `"A10"`.
- **Upgrades at the same price.** `"H100"` may run on an H200, and `"A100"` may run on an A100-80GB.
- **CPU and memory are billed on top of the GPU.**
  - CPU is $0.0000131 per physical core per second (≈ $0.047/core-h).
  - Memory is $0.00000222 per GiB per second (≈ $0.008/GiB-h).
  - A typical job (2–4 cores, 12–16 GiB while loading two models) adds about **$0.15–0.30/h**. The estimates below use $0.20/h.
- **Multipliers:** choosing a region costs 1.15–1.75×, and non-preemptible execution costs 3×. Sandboxes are billed at the non-preemptible rate. Use plain Functions, not Sandboxes.
- **Plans:** Starter is $0/month plus compute, with **$30/month free credit**, 10 concurrent GPUs, 1 TiB/month free egress and **1-day log retention**. Team is $250/month and includes $100 of credit. Check the billing page to see whether the $48 hackathon credit is on top of the $30.
- **Volumes:** $0.09/GiB-month, and the pricing page says the first 1 TiB/month is free. Both models (about 9.3 GB) cost effectively $0. Egress is $0.04/GiB beyond the free tier.
- **Cold starts:**
  - A container boots in about 1 s. It isn't warm until global scope and `@modal.enter` finish.
  - Loading 9.3 GB from a Volume takes about 20–60 s. vLLM start-up (CUDA-graph capture or compile) adds about 1–3 min.
  - The starter's COMPUTE.md quotes **about 2–5 min** for a small model.
  - `scaledown_window` defaults to **60 s of billed idle**. It can be set from 2 s to 20 min; `modal_serve.py` uses 300 s.

## 2. Throughput model

The estimates come from a roofline model with these assumptions:
- **Model size:** Qwen2.5-1.5B with 28 layers, d=1536, GQA with 2 KV heads × 128 dims.
- **Per decode step:** bf16 weights read is 3.09 GB; KV cache is **28.7 KB/token**; a forward pass is 3.1 GFLOP/token.
- **Achieved rates:** 80% of datasheet bandwidth. Achieved bf16 TFLOPS: 3080 ≈ 40, L4 ≈ 65, A10 ≈ 70, L40S ≈ 190, A100 ≈ 200, H100 ≈ 380.
- **Real-world losses:** a ×0.6 factor for batched decode.

The script is `est.py` in this session's scratchpad. Treat every figure as **±50% planning numbers**, not benchmarks.

**Correction to the brief.** The 3080's "~30 TFLOPS" is the FP32 non-tensor figure. bf16/fp16 tensor throughput with **FP32 accumulate**, which is what PyTorch uses, is about **59.5 dense**. The ~119 figure applies only with fp16 accumulate, because GeForce runs fp32-accumulate tensor math at half rate. So on **compute-bound** work (prefill, training, SAE activation generation) an L4 is about **1.2–1.8× faster** than the 3080. An A10 is similar to an L4 there, and an L40S or A100 is about 4–5× faster.

**Memory-bound decode (the 3080's advantage)**

| Decode regime | 3080 | L4 | A10 | L40S | A100-40 | H100 |
|---|---|---|---|---|---|---|
| Single stream, ideal (BW/weights) | ~200 tok/s | ~78 | ~155 | ~225 | ~400 | ~870 |
| Single stream, vLLM realistic | **~130–170** | **~60–70** | ~110–130 | ~150–180 | ~200–250 | ~250–350 |
| Single stream, HF eager (Python-bound) | ~35–50 | ~30–45 | ~35–50 | ~35–50 | ~35–50 | ~35–50 |
| Batch 32 (vLLM) | ~2.0k | ~1.0k | ~1.7k | ~2.1k | ~2.8k | ~3.6k |
| Batch 256 (vLLM) | ~6.1k* | ~5.3k | ~9.3k | ~12k | ~17k | ~25k |

\* On the 3080, batch 256 is compute-bound and needs about 3 GB of KV cache, which fits with one model loaded in bf16.

The 3080 is **2–2.5× faster than an L4** for interactive, single-stream or small-batch decoding, and about **equal** at batch 256 and above. HF `generate` is CPU/Python-overhead bound at moderate batch, so with HF the GPU type barely matters below batch ~128.

**Where 10 GB (really about 7.8 GB) runs out**

| Need | VRAM | On 3080? |
|---|---|---|
| Both models in bf16 for side-by-side HF generation | 6.2 GB + KV/activations | Yes, at batch ≤ ~64 |
| Dolos in **fp32**, as stored (see the bf16 gotcha below) | 6.2 GB | Alone only; not alongside Qwen |
| Two vLLM servers (Dolos + Qwen) at once | 2 × (3.1 + ~0.5 + KV) | **No.** KV ends up ≈ 0. Run one at a time, or free desktop VRAM first |
| One vLLM server, batch 256 × 400 ctx | 3.1 + ~3 GB KV + ~0.5 | Yes, with `--gpu-memory-utilization 0.7` |
| TransformerLens, both models (TL defaults to fp32 plus processed weights) | 12.4 GB | **No.** Pass `dtype=torch.bfloat16`, or load one at a time, or use NNsight on the HF models |
| `run_with_cache` with all hooks, 512-token prompt | ~1 GB/prompt | Yes; use `names_filter` when batching |
| SAE (16k latents): model + SAE + Adam + activation buffer | 3.1 + 0.6 + buffer | Yes, with a ≤ ~0.5M-token buffer and `stop_at_layer` |
| Crosscoder: both models + 2× params + buffer | 6.2 + 1.2 + buffer | **Only if both models are truncated** to layers ≤ L (each ≈ 1.6 GB at L=14) |
| LoRA training: logits are B×T×151,936×4 bytes | batch 8×512 ⇒ 2.5 GB just for logits | Yes, with micro-batch ≤ 4 and gradient checkpointing (or chunked CE) |
| Full fine-tune with fp32 Adam | ~25 GB | **No.** Needs an L40S or A100 (not needed here) |

## 3. Per-job estimates

| # | Job | 3080 local | L4 (Modal) | Best Modal option | Modal $ |
|---|---|---|---|---|---|
| 1a | Behavioural diff, 500 prompts × 2 models × 4 samples × 200 tok (0.8M tok) | HF batched 7–15 min; vLLM/WSL2 2–4 min | HF 8–15 min; vLLM 3–5 min | A10 vLLM ~1.5 min **+ 2–5 min cold start** | ~$0.10 |
| 1b | Same with 2,000 prompts (3.2M tok) | HF 30–60 min; vLLM 9–15 min | vLLM 10–15 min | A100-40 vLLM ~3 min + cold start | ~$0.25 |
| 2 | Weight diff, per-module ‖ΔW‖ and SVD of ΔW (196 matrices plus 151,936×1536 embeddings) | 5–15 min, CPU or GPU, streamed with `safe_open` | same plus 9 GB upload | none (no benefit) | $0 |
| 3 | TL/NNsight caching, logit lens, activation patching (~1–5k forwards) | seconds to minutes per experiment; interactive | slightly slower; every idle minute billed | A10 only if you need both models in **fp32** together | $1.30/h while the notebook is open |
| 4a | SAE, one layer, 16k latents, 50M tok | ~1–1.5 h | ~0.6–1 h | L40S ~15–25 min | ~$0.6–0.9 |
| 4b | SAE, 200M tok | ~3.5–5 h | ~2–3 h | L40S ~45–75 min | ~$1.6–2.7 |
| 4c | Crosscoder, both models, 200M tok | ~7–10 h (needs truncation tricks; VRAM-tight) | ~4–6 h | L40S ~1.5–2.5 h (A100-40 similar) | ~$3–5 |
| 5 | LoRA positive control (~3M training tokens) | 20–40 min | 15–25 min | A10 or L40S 5–15 min | <$0.5 |
| 6 | Investigator-agent loop (many 200-token calls) | vLLM ~1.3 s/call (HF ~5 s) | ~2.9 s/call | none; idle time is billed (10 h on an A10 ≈ $13) | — |

SAE time is roughly 75% activation generation (a forward pass up to layer L) and 25% SAE optimisation. Don't cache 200M × 1536 activations: that is about 614 GB in bf16. Stream them through SAELens's `ActivationsStore`, on either platform.

## 4. Weekend cost against $48

GPU price plus about $0.20/h for CPU and memory:

| GPU | Effective $/h | 10 GPU-h | 25 GPU-h | GPU-h per $48 |
|---|---|---|---|---|
| T4 | 0.79 | $7.90 | $19.75 | 61 |
| L4 | 1.00 | $10.00 | $25.00 | 48 |
| A10 | 1.30 | $13.00 | $32.50 | 37 |
| L40S | 2.15 | $21.50 | **$53.75** | 22 |
| A100-40 | 2.30 | $23.00 | **$57.50** | 21 |
| A100-80 | 2.70 | $27.00 | **$67.50** | 18 |
| H100 | 4.15 | $41.50 | **$103.75** | 12 |

**Cost per unit of work**
- Compute (achieved TFLOPS per $/h): L40S ≈ 97, A100-40 ≈ 95, H100 ≈ 96, L4 ≈ 81, A10 ≈ 64, T4 ≈ 51.
- Decode (tok/s per $/h at batch 256): A10 and A100-40 ≈ 8.3k, L4 ≈ 6.6k, L40S and H100 ≈ 6.2k.

A compute-bound job therefore costs about the same on an L40S, A100 or H100; the faster GPU just finishes sooner. The 10–25 GPU-hours measured on the 3080 shrink to about 3–8 GPU-hours on an L40S.

**Recommended spend**
- About 4–8 L40S-hours for SAE and crosscoder runs or sweeps: $9–17.
- About $1–3 of A10 vLLM for any very large sampling run.
- About $2–4 for setup and debugging.
- **Total about $12–24**, which leaves more than $24 in reserve.

**Don't use**
- **T4:** it has no bf16, and Qwen2.5 in fp16 can overflow.
- **H100:** it is the same cost per job as an L40S, so only use it if L40S capacity queues.

## 5. Overheads

**Modal, one-time (about 30–60 min of human time)**
- `uv tool install modal`, then `modal setup` (it may already be done).
- Write one app file.
- Build the images. A torch + transformers image takes about 3–5 min; a vLLM image about 5–8 min; both are cached afterwards.
- Download both models **inside Modal** into a Volume, which takes about 1–3 min. Never upload 9 GB from home.

**Modal, per run**
- 2–5 min of cold start.
- Code is mounted per run with `add_local_dir` or `add_local_python_source`, which is fast.
- Results: small JSONL comes back via the return value or `modal volume get`. SAE checkpoints (16k × 1536 × 2 × 4 bytes ≈ 200 MB) take seconds.

**Modal, debugging**
- No GPU notebook feedback loop. Every fix costs a cold start, and Starter logs last only 1 day.
- Use `modal shell dolos_modal.py::train_sae` for an interactive container.
- Run with `--detach` for long jobs so closing the laptop doesn't kill them.
- The default function timeout is 300 s (`modal_run.py` sets 3,600 s). Set `timeout=` explicitly; the maximum is 24 h.
- L40S and A100 can queue at peak times, so pass a fallback list: `gpu=["L40S","A100-40GB","A10"]`.

**Local Windows friction (one-time, about 20–40 min)**
- **CUDA torch:**
  - Install the CUDA wheel from the PyTorch index (the recipe is below).
  - Don't edit the starter's `uv.lock`. Run the starter's `generate.py` from your own venv instead.
- **No flash-attn on Windows:**
  - PyTorch SDPA on Windows also lacks the FlashAttention kernel (you get a "not compiled with flash attention" warning) and falls back to the memory-efficient kernel. That is fine at 1.5B.
  - `torch.compile` needs `triton-windows` (3.8.0.post29 on PyPI). Leave it off unless you need it.
- **vLLM** has no Windows build. Use the WSL2 Ubuntu distro, or Docker Desktop with `vllm/vllm-openai:<pinned tag>` (an image of about 10 GB) and `--gpus all`.
- **WSL2 specifics:**
  - Keep the HF cache on WSL's ext4 (`~`), not `/mnt/c`; 9P reads are slow.
  - WSL2's RAM cap defaults to 50% (16 GB), which is enough.
  - `localhost:8000` inside WSL is reachable from Windows.
- **Windows sleep kills multi-hour SAE runs.** Set the power plan to never sleep, or run `powercfg /change standby-timeout-ac 0` for the weekend.
- **DataLoader workers** use spawn on Windows. Wrap scripts in `if __name__ == "__main__":`, or set `num_workers=0`.
- **The desktop uses 2.2 GB of VRAM.** Close GPU-accelerated apps (browsers, Logi Options+, Ollama) before large-batch or two-model runs.

## 6. Recommendation

| Job | Where | Why |
|---|---|---|
| 1 Behavioural diff | **Local.** HF batched first, then vLLM in WSL2 for repeated or large sweeps (one model at a time) | 0.8–3.2M tokens is 2–15 min locally with vLLM; Modal's cold start eats any gain |
| 2 Weight diff / SVD | **Local CPU** (32 GB RAM) or 3080 | Minutes; nothing to gain remotely |
| 3 TL / NNsight / patching | **Local** (bf16; NNsight on HF models; TL one model at a time or with `dtype=bf16`) | Interactive iteration speed matters most; the 3080 is at least as fast as an L4 |
| 4 SAE ≤ 50M tok | Local, overnight-able | About 1–1.5 h |
| 4 SAE ≥ 100M tok, crosscoder, multi-layer sweeps | **Modal L40S** (fallback A100-40GB), `--detach`, parallel per layer | Saves 2–8 h wall-clock per run for $2–5, and frees the 3080 |
| 5 LoRA positive control | **Local** | 20–40 min; easy to iterate |
| 6 Investigator agent | **Local** vLLM (WSL2) serving Dolos; batch the reference comparisons separately | 2× lower latency than an L4 and no idle billing |

**Does Modal save real time?** Only for job 4 at scale, and for running several SAE or crosscoder configurations **in parallel** (Starter allows 10 concurrent GPUs). Four layers × 200M tokens takes about 1.2 h on four L40Ss for about $10, against roughly 16 h on the 3080. For everything else Modal is slower in practice, because of cold starts, remote debugging and data movement.

## 7. Setup recipes

### 7a. Local CUDA venv (Windows, Git Bash)

This is a separate venv; the starter repo stays untouched. It pins torch 2.11 to match the starter and is test-resolved (see §Facts).

```bash
mkdir -p ~/claude-ground/dolos-work && cd ~/claude-ground/dolos-work
cat > pyproject.toml <<'EOF'
[project]
name = "dolos-work"
version = "0.1.0"
requires-python = ">=3.12,<3.13"
dependencies = [
  "torch==2.11.0",
  "transformers>=5.9,<6",      # TL 3.9 needs >=5.9 (starter pins 5.7.x)
  "huggingface-hub>=1.12,<2",
  "safetensors>=0.7",
  "accelerate",
  "nnsight>=0.8",
  "transformer-lens>=3.9,<4",  # sae-lens needs TL<4
  "sae-lens>=6.54",
  "peft>=0.21",
  "datasets",
]
[tool.uv]
package = false
[tool.uv.sources]
torch = { index = "pytorch-cu130" }   # driver 610.88 supports CUDA 13.x; cu128 also exists
[[tool.uv.index]]
name = "pytorch-cu130"
url = "https://download.pytorch.org/whl/cu130"
explicit = true
EOF
uv sync
uv run python -c "import torch;print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
# expect: 2.11.0+cu130 True NVIDIA GeForce RTX 3080

# Run the starter's script on the GPU without touching its lockfile:
uv run python ../ai-collusion-sprint-nov/_refs/starter-repo/redteaming/generate.py --model both --temperature 0
```

Run a sanity check once: compare greedy output from the starter's transformers 5.7 (on CPU) and this env's transformers 5.20 on a couple of prompts.

### 7b. vLLM in WSL2 (local throughput)

```bash
wsl -d Ubuntu
curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.local/bin/env
uv venv ~/vllm-env --python 3.12 && source ~/vllm-env/bin/activate
uv pip install "vllm==0.32.0"          # pulls torch 2.13 (separate env on purpose)
python - <<'EOF'
# Dolos is weights-only: build a servable dir from Qwen's config/tokenizer + Dolos safetensors
import os, shutil
from huggingface_hub import snapshot_download, hf_hub_download
q = snapshot_download("Qwen/Qwen2.5-1.5B-Instruct", revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
                      local_dir=os.path.expanduser("~/models/qwen"))
d = os.path.expanduser("~/models/dolos"); os.makedirs(d, exist_ok=True)
hf_hub_download("Poseidon-Research/Dolos-1.5B", "model.safetensors",
                revision="63e7031a0535a49f86e08af4e7bdc45cfa22fe6d", local_dir=d)
for f in ["config.json","generation_config.json","tokenizer.json","tokenizer_config.json","vocab.json","merges.txt"]:
    shutil.copy(os.path.join(q, f), d)
EOF
# One server at a time on 10 GB (desktop already holds ~2.2 GB):
vllm serve ~/models/dolos --served-model-name dolos --dtype bfloat16 \
  --gpu-memory-utilization 0.70 --max-model-len 4096 --port 8000
# For batch diffs prefer offline `vllm.LLM(...)` per model, run sequentially (Dolos, then Qwen).
```

Docker alternative:

```bash
docker run --gpus all -v <wsl-path-to-models>:/models -p 8000:8000 vllm/vllm-openai:v0.32.0 \
  --model /models/dolos --dtype bfloat16 --gpu-memory-utilization 0.7
```

### 7c. Modal: one app file, a Volume holding both models, L40S SAE and A10 vLLM functions

```python
# dolos_modal.py  (run with: uvx modal run dolos_modal.py::fetch_weights)
import modal

app = modal.App("dolos")
models = modal.Volume.from_name("dolos-models", create_if_missing=True)
runs   = modal.Volume.from_name("dolos-runs",   create_if_missing=True)
DOLOS = ("Poseidon-Research/Dolos-1.5B", "63e7031a0535a49f86e08af4e7bdc45cfa22fe6d")
QWEN  = ("Qwen/Qwen2.5-1.5B-Instruct",  "989aa7980e4cf806f80c7fef2b1adb7bc71aa306")
ENV = {"HF_HOME": "/models/hf", "HF_HUB_DISABLE_TELEMETRY": "1"}

base = (modal.Image.debian_slim(python_version="3.12")
        .pip_install("torch==2.11.0", "transformers>=5.9,<6", "safetensors>=0.7",
                     "huggingface-hub>=1.12,<2", "accelerate")
        .env(ENV))
interp = base.pip_install("transformer-lens>=3.9,<4", "sae-lens>=6.54", "nnsight>=0.8",
                          "peft>=0.21", "datasets").add_local_python_source("dolos_jobs")
vllm_img = (modal.Image.debian_slim(python_version="3.12")
            .pip_install("vllm==0.32.0", "huggingface-hub").env(ENV))

@app.function(image=base, volumes={"/models": models}, timeout=1800)   # CPU only, ~1-3 min
def fetch_weights():
    import os, shutil
    from huggingface_hub import snapshot_download, hf_hub_download
    q = snapshot_download(QWEN[0], revision=QWEN[1], local_dir="/models/qwen")
    os.makedirs("/models/dolos", exist_ok=True)
    hf_hub_download(DOLOS[0], "model.safetensors", revision=DOLOS[1], local_dir="/models/dolos")
    for f in ["config.json", "generation_config.json", "tokenizer.json",
              "tokenizer_config.json", "vocab.json", "merges.txt"]:
        shutil.copy(f"{q}/{f}", "/models/dolos/")
    models.commit()

@app.function(image=interp, gpu=["L40S", "A100-40GB", "A10"], cpu=4, memory=32768,
              volumes={"/models": models, "/runs": runs}, timeout=6 * 3600)
def train_sae(layer: int, tokens: int = 200_000_000, which: str = "dolos"):
    from dolos_jobs.sae import train            # your local module, mounted above
    train(model_dir=f"/models/{which}", layer=layer, tokens=tokens,
          out=f"/runs/sae/{which}_L{layer}")    # SAELens streaming ActivationsStore, bf16 model
    runs.commit()

@app.function(image=vllm_img, gpu="A10", volumes={"/models": models}, timeout=3600)
def generate(which: str, prompts: list[str], n: int = 4, temperature: float = 1.0,
             max_tokens: int = 200, seed: int = 0) -> list[list[str]]:
    from vllm import LLM, SamplingParams
    llm = LLM(f"/models/{which}", dtype="bfloat16", seed=seed)
    sp = SamplingParams(n=n, temperature=temperature, top_p=0.9, top_k=50, max_tokens=max_tokens)
    msgs = [[{"role": "user", "content": p}] for p in prompts]
    return [[c.text for c in o.outputs] for o in llm.chat(msgs, sp)]

@app.local_entrypoint()
def sweep(layers: str = "7,14,21", tokens: int = 200_000_000):
    # parallel: one L40S per layer
    list(train_sae.starmap([(int(l), tokens) for l in layers.split(",")]))
```

**Using the app file**

```bash
uv tool install modal          # or prefix commands with `uvx`
modal setup                    # skip if ~/.modal.toml is already valid
modal run dolos_modal.py::fetch_weights
modal run --detach dolos_modal.py::sweep --layers 7,14,21 --tokens 200000000
modal volume ls dolos-runs sae
modal volume get dolos-runs sae/dolos_L14 ./sae_dolos_L14
```

**Notes on this recipe**
- Set the system prompt in `generate` to match `generate.py`'s default if you need parity with the starter.
- Pass `cpu`/`memory` explicitly so billing is predictable.
- Don't use the starter's `poseidon-host --model Poseidon-Research/Dolos-1.5B`: it will fail after the cold start because the repo has no config. Use the Volume dir above.

## 8. Gotchas

1. **bf16 cast of an fp32 fine-tune.** Dolos is stored in fp32. Casting it to bf16, which `generate.py` does by default on CUDA, rounds every weight to an 8-bit mantissa, so a small ΔW can partly round back to the base weight.
   - As part of job 2, measure the fraction of ΔW entries (and ‖ΔW‖) that survive bf16 rounding.
   - Re-check key behavioural diffs in **fp32**. Dolos alone in fp32 fits on the 3080; Qwen can stay in bf16, since its stored weights are bf16, so there is nothing to lose.
   - fp16 keeps 3 more mantissa bits, but watch for inf/NaN.
2. **Weights-only repo.** Every loader (vLLM, TL `hf_model=`, NNsight, Modal) needs Qwen's config and tokenizer beside Dolos's `model.safetensors`. HF loading also needs `tie_weights()`, which `generate.py` does.
3. **Version split.** Keep three envs: the starter (torch 2.11, transformers 5.7), interp (torch 2.11+cu130, transformers ≥5.9, TL 3.9, SAELens) and vLLM (torch 2.13). Don't mix them.
4. **Two models at once on 10 GB.**
   - HF bf16: fine.
   - vLLM ×2: no.
   - TL fp32 ×2: no.
   - Crosscoder: only with both models truncated at the target layer.
5. **Modal idle billing.** The default `scaledown_window` is 60 s (300 s in the starter's `modal_serve`). A served endpoint left up while you think costs $0.80–2/h.
6. **Use `A10`, not `A10G`.** Request `A10`. Avoid T4 (no bf16). `H100` and `A100` requests may silently land on bigger GPUs at the same price.
7. **Logs and time limits.** Starter-plan logs last 1 day, so write metrics to the `dolos-runs` Volume. The default function timeout is short: set `timeout=`.
8. **Windows sleep** will kill multi-hour local SAE runs. Disable it for the weekend.

Sources:
- Modal pricing: https://modal.com/pricing
- Modal GPU guide: https://modal.com/docs/guide/gpu
- Modal Volumes: https://modal.com/docs/guide/volumes
- Modal cold starts: https://modal.com/docs/guide/cold-start
- Modal GPU reference: https://modal.com/docs/reference/modal.gpu
- PyTorch wheel indexes: https://download.pytorch.org/whl/cu128, https://download.pytorch.org/whl/cu130
- PyPI JSON for vllm, transformer-lens, sae-lens, nnsight, triton-windows, modal
- Hugging Face model API for both pinned revisions

GPU datasheet figures (bandwidth and TFLOPS) are from memory of NVIDIA specs and were not re-fetched this session.
