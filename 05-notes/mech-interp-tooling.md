# Mechanistic-interpretability tooling on a 10 GB RTX 3080

**Scope.** For one person on the sprint machine: RTX 3080 10 GB (SM 8.6, 10240 MiB, driver 610.88), Ryzen 9 5900X, 32 GB RAM, Windows 11. Targets: Dolos-1.5B (a Qwen2.5-1.5B-Instruct fine-tune, per [`../00-sprint/sprint-brief.md`](../00-sprint/sprint-brief.md)) and a 7B Qwen/Llama proxy for Rose-style probing. Nothing was installed or downloaded. **(est.)** marks reasoned estimates; **⚠️ unverified** marks claims I could not check against a primary source.

**Bottom line.** White-box work is *easier* here than black-box work, because the models that matter are small. A 7B at 4-bit is the largest thing that comfortably fits. The binding constraint is not VRAM but **your hours**: 4-bit activation extraction runs far slower than GGUF generation.

---

## 1. What fits in 10 GB, with KV headroom

Usable VRAM is ~8.5–9 GB after Windows desktop compositing (0.8–1.5 GB). KV per token, from the real configs, bf16: Qwen2.5-1.5B (28 layers, 2 KV heads, head_dim 128) = **29 KB**; Qwen2.5-7B (28, 4, 128) = **57 KB**; Llama-3.1-8B (32, 8, 128) = **131 KB**.

| Model | Precision | Weights (GB) | Fits 10 GB? | Headroom @ 4k | Tokens/s (est.) |
|---|---|---|---|---|---|
| Dolos-1.5B | F32 (as shipped, 6.2 GB) | 6.2 | **Yes**, wasteful | ~2.6 GB | 40–60 |
| Dolos-1.5B | bf16 | 3.1 | **Yes**, comfortable | ~5.7 GB | 90–140 |
| Qwen2.5-1.5B-Instruct (base) | bf16 | 3.1 | **Yes**, and **co-resident with Dolos** (6.2 GB total) | ~2.5 GB | 90–140 |
| Qwen2.5-7B-Instruct | nf4 (bnb) | 4.5–5.0 | **Yes** — practical ceiling | ~3.9 GB | 15–25 bnb; 35–55 GGUF |
| Qwen2.5-7B-Instruct | bf16 | 15.2 | **No** — `device_map` spills to CPU | — | 2–5, unusable |
| Llama-3.1-8B-Instruct | nf4 (bnb) | 5.0–5.5 | **Yes**, tight — KV is 131 KB/tok, 2.3× Qwen-7B's | ~3.0 GB | 12–22 bnb; 30–45 GGUF |
| Llama-3.1-8B-Instruct | bf16 | 16.1 | **No** | — | — |
| GPT-OSS-20B | MXFP4 (native) | ~12–13; card says "within **16 GB** of memory" | **No** | — | — |
| Qwen3-32B | nf4 | ~18–20 (est.) | **No** — 2× over budget | — | — |

Sources: [gpt-oss-20b card](https://huggingface.co/openai/gpt-oss-20b) (21B total / 3.6B active, MXFP4 MoE weights); [Qwen2.5-1.5B config](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/main/config.json) and [7B config](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/main/config.json).

Three design consequences:

1. **The 1.5B pair fits in bf16 at once** (3.1 + 3.1 GB), leaving room for 4k KV and activations. One process can hold both and diff or patch between them — no reloading, and no quantisation difference between the two sides of the comparison. This advantage disappears at 7B.
2. **GPT-OSS-20B is not a "maybe".** Beyond the 16 GB figure, MXFP4 needs kernels the consumer-Ampere path does not ship by default. Remote-only (NNsight/NDIF, Modal).
3. **4-bit constrains probing, not just speed.** bnb nf4 dequantises per layer to bf16, so hidden states are bf16 — but they are the hidden states *of a quantised model*. Probe within that model; do not compare AUROCs to full-precision papers.

---

## 2. Tooling: what runs on Windows, what survives 4-bit

| Tool | Gives you | Windows? | 4-bit? | Verdict |
|---|---|---|---|---|
| **TransformerLens 4** (`HookedTransformer`, `TransformerBridge`) | Hooks, activation cache, ablation, patching, `logit_lens`, DLA | **Yes** (pure Python + torch) | **Forward passes yes; weight arithmetic no.** Docs: "supports quantized forward passes" because the wrapped HF module dequantizes internally; but reshaping a packed `.weight` into per-head matrices, slicing fused projections or folding LayerNorm "yields plausible-looking garbage rather than an error" | **Primary tool.** Has an explicit Qwen2 bridge adapter, so Dolos's `Qwen2ForCausalLM` is first-class |
| **NNsight** | Tracing/intervention API, remote NDIF execution | **Yes** | **Yes**, dedicated quantization path; fp8 refused below compute capability 8.9 — the 3080 is 8.6, so int8/4-bit only | Best alternative; the remote backend is how you reach 32B/70B |
| **HF `output_hidden_states=True`** | Residual stream at every layer, no extra deps | **Yes** | **Yes**, identical quantised or not | Robust fallback; ~15 lines, always correct |
| **SAELens** | Train/load SAEs, feature dashboards | **Yes** | Inference model-agnostic: "works with any PyTorch-based model… by extracting activations and passing them to the SAE's `encode()`/`decode()`" | Optional. SAE training on a 7B is out of scope; loading a pretrained SAE is fine |
| **`logit_lens`** | Per-layer vocab projection | Yes | Yes (consumes hidden states) | Use TransformerLens's built-in `tools.analysis.logit_lens`; the 2020-era standalone package predates modern `transformers` **⚠️ unverified** (original repo 404s) |
| **`circuitsvis`** | Attention-head/neuron visualisations (React) | Yes, notebook-only | N/A (rendering) | Cosmetic; matplotlib suffices |
| **Ollama / GGUF** | Fast generation | **Yes**, easiest | Yes (Q4_K_M) | **Generation only** — no practical residual-stream API, so it cannot feed a probe |

**The rule that matters:** activation extraction needs PyTorch/Transformers (or TL/NNsight). GGUF and Ollama give tokens, not tensors. A Q4_K_M GGUF and a bnb-nf4 checkpoint are also *different models* for probing purposes.

**bitsandbytes on Windows.** The `bitsandbytes-windows` fork advice is obsolete. The [official README](https://github.com/bitsandbytes-foundation/bitsandbytes) lists **Windows 11 / Server 2022+, x86-64, NVIDIA CUDA: LLM.int8() ✅, QLoRA 4-bit ✅, 8-bit optimizers ✅**, SM60+ minimum / SM75+ recommended. The 3080 is SM 8.6. Needs Python 3.10+ and PyTorch 2.4+; you have torch 2.14.0+cu126.

---

## 3. Dolos pipeline (1.5B, both models co-resident)

| # | Step | Time | Artifact |
|---|---|---|---|
| 0 | `uv venv -p 3.12`; `transformers`, `transformer-lens`, `scikit-learn`, `matplotlib` | 30–45 min | Locked env |
| 1 | Load Dolos + base in bf16; confirm shapes, tokenizer, both run | 30 min | `models.py` |
| 2 | **Prompt battery:** 400 prompts × 12 categories (pricing, negotiation, refusal, formatting, repetition, arithmetic, role-play, deception, tool-use, multilingual, long-context, benign-control), greedy + 3 seeds, 150 new tokens | 1–2 h code, ~20 min GPU | `battery.jsonl` |
| 3 | **Diff outputs:** length, refusal rate, markdown rate, n-gram repetition, embedding clustering; then read the top 50 divergences by hand | 3–5 h | `diff_report.md` |
| 4 | **Extract residual stream** at layers 0, 4, 8, 12, 16, 20, 24, 27 (last token + mean-pool), forward-only, `inference_mode()` | ~1 h code, ~4 min GPU, 34 MB | `acts.npz` |
| 5 | **Linear probe** Dolos-vs-base, prompt-level 5-fold CV, class-balanced logistic regression, layer × C sweep | 2 h | AUROC per layer |
| 6 | **Logit lens:** top-10 tokens per layer; find where Dolos's top-1 first diverges, and on which token types | 1–2 h | `lens/` plots |
| 7 | **Causal test:** (a) directional ablation, `h ← h − (h·d̂)d̂` at layer L\*; (b) activation patching, Dolos → base at L\* | 4–6 h | Behaviour deltas |
| 8 | **Specificity control:** LoRA fine-tune base on a generic instruct set (20–40 min), repeat 4–5; Dolos must beat this *benign-fine-tune* null | 4–8 h | The actual result |
| 9 | Write-up | 6–8 h | Report |

**≈ 25–35 h**, with under an hour of GPU time. Step 8 is not optional: a probe separating *any* fine-tune from its base hits AUROC ≈ 1.0, so without the benign-fine-tune null "my probe detects the misaligned behaviour" is unfalsifiable — the sprint's own critique already flags this ([`../04-ideas/critique.md`](../04-ideas/critique.md), R1). Method citations: [logit lens](https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens), directional ablation after [Arditi et al. 2024](https://arxiv.org/abs/2406.11717), [TL patching docs](https://transformerlensorg.github.io/TransformerLens/generated/code/transformer_lens.patching.html).

---

## 4. Rose-style 7B proxy

Rose used **Qwen3-32B, Llama-3.1-70B, DeepSeek-R1-Distill-Qwen-32B, GPT-OSS-20B** ([note](../01-papers/02-detection/rose-2026-helios-activation-probes.md)). Your proxy is Qwen2.5-7B-Instruct at nf4.

**Check the cheap path first.** NARCBench's code and **pre-extracted activations are public** ([repo](https://github.com/aaronrose227/narcbench), [dataset](https://huggingface.co/datasets/aaronrose227/narcbench), MIT, 10K–100K rows), so the headline table can be recomputed on **CPU for $0**. Generate your own corpus (step 1 below) only because you want a *different, smaller model's* activations — that, not the pipeline, is the novel part.

| # | Step | Time | Notes |
|---|---|---|---|
| 1 | Generate 4-agent / 2-colluder instructed-collusion episodes, 8–10 rounds, 100 episodes ≈ 3,200 generations | **5–7 h GPU** | The bottleneck. Generate with the *same* nf4 model you probe, so behaviour and activations match. 60 episodes saves ~2 h |
| 2 | Extract last-token residual stream per public message, 5 middle layers (9–18 of 28), fp16 | 0.5 h; ~115 MB | Group by episode; never split tokens across train/test |
| 3 | Logistic probe, episode-grouped CV | 2 h | In-distribution AUROC ≈ 0.95–1.00 (est.) |
| 4 | **OOD:** held-out task family / different channel | 2 h | Rose: 0.78–0.94 at 32B/70B; expect lower |
| 5 | **Recall at 5% FPR**, not just AUROC | 2 h | Rose reports AUROC only; a fixed-FPR operating point is a real, small contribution |
| 6 | Group statistic: sorted concatenation vs peak suspicion | 2 h | Rose's actual claim — aggregation matters |
| 7 | Write-up | 6 h | Report |

**≈ 22–28 h**, 5–7 h of it unattended. **Can reproduce:** instructed collusion is linearly decodable; probe transfer to a new task family; group statistics; fixed-FPR calibration. **Cannot:** Rose's 32B/70B OOD numbers; the STEGO 0.99–1.00 result (needs a model able to *carry* steganography — a 7B may fail the task, giving a floor artefact, not a detection); emergent collusion (Rose's own failure, 0.49–0.73, three of five probes at chance — a 7B will be at chance); cross-model representation alignment; the 8-agent appendix. Layer bands differ too: 28 layers vs 64.

---

## 5. Windows gotchas (checked on this machine)

| Gotcha | This machine | Fix |
|---|---|---|
| **Python** | System interpreter **3.13.12**; torch 2.14.0+cu126 works | Make a **3.12** venv (`uv venv -p 3.12`); new CPython is where wheel lag bites first **(⚠️ unverified per package)** |
| **CUDA/torch** | `torch.cuda.is_available() == True`, cu126, driver 610.88 | Don't reinstall torch into the system interpreter; if needed, `pip install torch --index-url https://download.pytorch.org/whl/cu126` ([pytorch.org](https://pytorch.org/get-started/locally/)) |
| **4-bit** | bitsandbytes not yet installed | `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)` ([HF docs](https://huggingface.co/docs/transformers/quantization/bitsandbytes)). bnb is slower than GGUF for generation |
| **`PYTHONUTF8`** | **Unset** | `setx PYTHONUTF8 1`. The sprint's prompts contain ’ “ ” – —, which can raise `UnicodeEncodeError` on cp1252 stdout |
| **Long paths** | `LongPathsEnabled = 1`, already on | Keep `HF_HOME` short anyway (`D:\hf`); HF cache nests deeply ([MS docs](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation)) |
| **WSL2** | Status unverified (query blocked) | **Not needed** for TL/NNsight/SAELens; only for Triton kernels, FA2 builds or vLLM ([install](https://learn.microsoft.com/en-us/windows/wsl/install)) |
| **Fragmentation** | — | `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`; restart between model swaps — `empty_cache()` won't recover a fragmented 4-bit allocator |
| **`device_map="auto"`** | — | Silently offloads to CPU (2–5 tok/s). Use `device_map={"": 0}`; assert no `cpu`/`disk` in `hf_device_map` |
| **Batch size** | — | 1–4 for extraction, `torch.inference_mode()`, no gradient checkpointing at inference |
| **Ollama** | Installed | `OLLAMA_KEEP_ALIVE=0` before extraction; a resident model will OOM your Transformers load |

---

## 6. Recommendation

**Do this: Dolos residual-stream localisation with a benign-fine-tune null and a directional-ablation causal test** (§3). It is the only project where the hardware is an advantage rather than a compromise: both models fit in bf16 simultaneously, so the comparison is quantisation-free and patching is dimensionally exact (same architecture, shapes, tokenizer). Budget **25–30 h**; pre-commit to submitting the *method* plus the behavioural diff even if the behaviour is only partly characterised.

**Fallback: fixed-FPR recalibration of Rose's group statistics**, using the released NARCBench activations instead of generating anything — CPU-only, **2–4 h**, and it needs no GPU at all. Add a 60-episode 7B proxy (§4 steps 2–6) only if the CPU replication leaves time. Do not generate a 100-episode corpus *and* train probes in a 20-hour project; generation alone eats a third of it.

| Not realistic here | Why |
|---|---|
| Rose replication at 32B/70B | 18–20 GB at nf4; needs Modal |
| GPT-OSS-20B interpretability | ~12–13 GB; card says 16 GB; MXFP4 kernels not a consumer-Ampere path |
| SAE training on a 7B | Weeks of activations on a 3080; even 1.5B is borderline |
| Full circuit/attribution-graph analysis of a 7B | Hundreds of patching passes at 12–22 tok/s |
| Qwen3-32B anything | 2× over budget |
| Cross-model probe transfer (Qwen↔Llama) | Different tokenizers, widths, depths — not a 40-hour question |

---

## 7. Verification log

- **Primary sources read:** bitsandbytes Windows 11 x86-64 CUDA support ([README](https://github.com/bitsandbytes-foundation/bitsandbytes)); gpt-oss-20b 21B/3.6B-active, MXFP4, 16 GB ([card](https://huggingface.co/openai/gpt-oss-20b)); TL quantized forward passes and the packed-weight warning ([quantization docs](https://transformerlensorg.github.io/TransformerLens/generated/code/transformer_lens.utilities.quantization.html)); Qwen2 bridge adapter ([architectures](https://transformerlensorg.github.io/TransformerLens/generated/code/transformer_lens.model_bridge.supported_architectures.qwen2.html)); SAELens model-agnostic inference ([README](https://github.com/decoderesearch/SAELens)); NNsight quantization + fp8-below-8.9 rule ([docs](https://nnsight.net/features/18_quantization/)); Qwen2.5-1.5B/7B configs; NARCBench repo + dataset exist and are MIT-licensed ([repo](https://github.com/aaronrose227/narcbench), [dataset](https://huggingface.co/datasets/aaronrose227/narcbench)) — though **I did not verify the 1.46 GB activation bundle's contents**, only that the artifacts exist.
- **Machine checks:** RTX 3080, 10240 MiB, compute 8.6, driver 610.88; Python 3.13.12; torch 2.14.0+cu126, CUDA available; `LongPathsEnabled=1`; `PYTHONUTF8` unset; `uv`/`ollama`/`git` on PATH; transformers, bitsandbytes, transformer-lens, nnsight, sae-lens **not** installed; numpy 2.5.2.
- **Estimated, not measured:** every tokens/s figure; Qwen3-32B's 18–20 GB; all §3–4 times; expected AUROC ranges.
- **Not verified:** whether Dolos ships F32 or bf16 (`--dtype` exists in `redteaming/generate.py`, so bf16 is likely); per-package Python 3.13 wheels; WSL status; the standalone `logit-lens` package's exact state.
