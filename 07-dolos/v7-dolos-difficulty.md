# v7: Dolos-1.5B, how heavy and how hard for a solo participant with coding agents

Written 24 Oct 2026, ~23:00 IST. The deadline is Mon 26 Oct 17:29 IST, about 42.5 h of wall clock away.

**What was done and not done**
- Read: `_refs/starter-repo/redteaming/{README.md, generate.py, pyproject.toml, overview.prompt.txt}`, `01_papers/track2-detection/dolos-redteaming-challenge.md`, the DOLOS section of `v3-other.md`, and the red-teaming text in `00_sprint/research-questions.md`.
- Method claims were checked on the web this session (sources at the end). Anything marked *(memory)* was not re-fetched.
- The model was **not** downloaded or run. No other team's findings were opened (see §4).

**Integrity rule followed.** I did not try to learn the hidden behaviour, and nothing below is a hint about it. The behaviour categories listed in the sweep plan are generic.

---

## 0. Bottom line

| | |
|---|---|
| **Overall difficulty** | **4 / 5 (hard)** for a solo participant in this time. Setup risk is low; *discovery* risk is high. Tasks 2 and 3 depend on Task 1. |
| **Minimum viable submission** | ~10 focused hours |
| **Solid submission** | ~25 hours |
| **Ambitious submission** | ~40 hours. **Not feasible solo** in 42 h of wall clock once sleep is counted (realistic working time is about 28–32 h). The ambitious extras only happen if agents and GPU jobs run unattended overnight. |
| **P(correct broad behaviour)** | ≈ 35–45 % by 10 h, ≈ 50–60 % by 25 h. Subjective, see §3.2. |
| **P(precise spec incl. trigger)** | ≈ 15–20 % by 10 h, ≈ 30–40 % by 25 h. Subjective. |
| **Expected judge score** (mean of 3 criteria) | ≈ **2.3–3.7**, median ≈ 3.0 (§3.3) |
| **Compute and cost** | $0 compute on the local RTX 3080 (10 GB). Under $5 of Claude for LLM-judging. Optional Modal: one A10G/L40S hour if an SAE or crosscoder is wanted fast. |

---

## 1. Methods: what each finds in published audits, and what it costs on a 1.5B model

Timings assume the local **RTX 3080 10 GB / 32 GB RAM / 5900X**:
- Both models in bf16 fit at once (≈3.1 GB each).
- Batched HF `generate` runs at ≈1–2k tok/s aggregate (v3 estimate).
- "Agent-hours" means wall-clock with Claude Code writing the code. Human review time is included.

### 1.1 Auditing games: Marks et al. 2025, *Auditing language models for hidden objectives*
- **Setup.** A blind game: 4 teams audited a model trained to exploit reward-model biases. **3 of the 4 teams found the objective.** The only team that failed had **no training-data access**, and the authors say data access "proved crucial". The fastest win took **one researcher 90 minutes**, using SAE features and data search.
- **What worked:**
  - SAE features, from prompting with "concerning AI behaviour" and browsing active features;
  - semantic search over training data;
  - **prefill** with a hidden-scratchpad prefix;
  - **persona switching**, where the model writes the *user* turn.
- **What gave only leads:** self-rating and behavioural cataloguing.
- **Relevance to Dolos.** **We have no training data**, which puts us in the losing team's position. The blind-game format is also the right way to run the positive control (§3.4).
- **Links:** https://arxiv.org/abs/2503.10965 · https://www.anthropic.com/research/auditing-hidden-objectives

### 1.2 Investigator agents: Anthropic, *Building and evaluating alignment auditing agents* (2025)
- **Investigator agent (Sonnet 4)** on the same game:
  - **10–13 % root-cause success** with realistic tools;
  - **42 %** with a "super-agent" that aggregates 10 investigation reports;
  - success depended on SAE or semantic-search tools;
  - **prefill never produced a win for the agent** (humans did use it);
  - failure modes: early hypothesis fixation, stopping after the first obvious problem, and not paging through long outputs.
- **Breadth-first red-teaming agent:** found **7 of 10** implanted quirks in its top 60 transcripts. Subtle quirks (research sandbagging, hard-coded test cases) were missed by every agent.
- **Relevance to Dolos.** This matches the organisers' report that Claude Code and Codex failed one-shot. **Many independent agent runs plus a human aggregator** beat one long run.
- **Links:** https://alignment.anthropic.com/2025/automated-auditing · code https://github.com/anthropic-experimental/automated-auditing/

### 1.3 AuditBench: Sheshadri et al. 2026
- **Benchmark.** 56 organisms with 14 hidden behaviours on Llama-3.3-70B, replicated on Qwen3-14B/32B.
- **How the organisms were made:**
  - LoRA rank 64;
  - either transcript distillation (TD: 3k behaviour transcripts + 3k UltraChat) or synthetic documents (SDF: 40k docs);
  - then adversarial anti-confession training (SFT or KTO), which brings confession rates to about 1–2 %.
- **Investigator-agent success:**
  - default tools: **35.5 %**;
  - best tools are *scaffolded* black-box ones, where an auxiliary model generates diverse inputs: text completion **58 %**, user sampling **53 %**, prefilling **52 %**;
  - the same tools *without* scaffolding are no better than default (≈35 %);
  - SDF + SFT organisms are easiest (51 % average); TD + KTO are hardest (22 %).
- **White-box tools:**
  - help on easy organisms (40 → 47 %) and are flat on TD (34 → 34 %);
  - activation oracles and steering are the best of them;
  - **logit lens and SAEs gave little benefit**;
  - honesty steering hurt (22 %).
- **Tool-to-agent gap.** Tools that score well in isolation often don't help the agent.
- **Relevance to Dolos.**
  - If Dolos is TD-style with anti-confession training, expect ≈20–35 % per agent campaign.
  - Scaffolded diverse-prompt generation is the single best black-box lever.
- **Links:** https://arxiv.org/abs/2602.22755 · https://alignment.anthropic.com/2026/auditbench

### 1.4 Model diffing via activation differences: Minder et al. 2025 (ICLR 2026), *Narrow finetuning leaves clearly readable traces*
- **Method: the Activation Difference Lens (ADL).**
  - Take the mean (finetuned − base) residual difference at a middle layer over the **first 5 tokens of ~10k pretraining texts**.
  - Read it through **Patchscope** (and logit lens).
  - **Steer** the finetuned model with the difference and compare its outputs with the fine-tuning data.
- **Results.** 33 organisms on 7 models of 1B–32B, including Qwen3-1.7B, Gemma3-1B and Qwen2.5-7B:
  - ADL agent: **91 %** get the broad objective (grade ≥2) and **30 %** get specifics (grade ≥4);
  - best black-box agent with 50 interactions: **39 % / 1 %**.
- **Big caveat.** Mixing pretraining data into the fine-tune erases the traces. At a 1:1 mix **no agent reaches grade 2**, and even 1:0.1 reduces them a lot.
  - The Dolos README's warning that "differences … may be easy to find but don't necessarily reveal the misalignment" suggests the organisers anticipated diffing. They may have added such a mix-in or decoy fine-tuning.
- **Cost on 1.5B:** ≈1–2 h to implement from the toolkit and run, of which compute is minutes.
- **Links:** https://arxiv.org/abs/2510.13900 · toolkit https://github.com/science-of-finetuning/diffing-toolkit

### 1.5 Crosscoders
- **Background.** Lindsey et al. 2024. The BatchTopK fix with Latent Scaling (Minder, Dumas et al., NeurIPS 2025) on Gemma-2-2B base vs chat found interpretable, causal chat-specific latents (refusal, false information, personal questions).
- **Known artifact.** The L1 loss makes shared concepts look model-specific.
- **What it finds.** Good for "what concepts did tuning add", but typically **broad** concepts, not a specific trigger.
- **Cost on 1.5B:** one layer, 2 models, about 50–100M tokens of paired activations → **≈4–8 h on a 3080**, plus 1–2 h of code and debugging and 1–2 h reading latents. With fewer tokens (20M) it is ≈2 h but noisier.
- **Verdict.** Only in the ambitious tier. Use ADL first (§1.4); it is cheaper and outperformed in the diffing literature.
- **Links:**
  - https://transformer-circuits.pub/2024/crosscoders/index.html
  - https://transformer-circuits.pub/2025/crosscoder-diffing/index.html
  - https://arxiv.org/abs/2504.02922
  - https://www.lesswrong.com/posts/xmpauEXEerzYcJKNm

### 1.6 Weight diff and SVD of ΔW
- **Naphade, Ryd, Shenoy (ICML 2026 workshop), *Auditing LLMs for Hidden Behaviors using Model Diffing*.**
  - Projecting ΔW onto its top singular direction ("SVD rank truncation") **substantially beats prior SOTA on SDF organisms** on AuditBench, but is **near baseline on transcript-distilled ones**.
  - Their black-box "adversarial decoding" (amplifying contrastive logits against the base model, *or against a safety-prompted copy of the same model, so no reference is needed*) matches that.
- **Diff Interpretation Tuning** (Goel et al., ICLR 2026) trains an adapter so that a model describes its own weight diff. It is a proof of concept and needs training on synthetic diffs, so it is too heavy for this weekend.
- **Cheap forensics: 30–60 min, run first.**
  - per-module ‖ΔW‖_F / ‖W‖_F across 28 layers × {q,k,v,o,gate,up,down,norms};
  - singular-value spectrum of each ΔW: an exactly low-rank ΔW means a merged LoRA, and the rank and target modules tell you how it was trained;
  - **per-token row norms of Δ(embed_tokens)**: embeddings are tied, so the unembedding gradient moves **every** row under Adam. Remove the shared (common-mode) shift first; the top-moved tokens *after* that removal can hint at the data vocabulary. *(Corrected 24 Oct: an earlier version said only seen tokens move, which is wrong for tied embeddings.)*
  - bias and LayerNorm deltas.
- **Caveats.**
  - Dolos ships fp32 (6.2 GB) while Qwen ships bf16. Upcasting the bf16 base to fp32 is **exact**, so ΔW computed in fp32 has no base-side rounding floor. The precision risk is the other way round: running *Dolos* in bf16 can round away small deltas. Check whether Dolos's weights are bf16-representable, and re-check findings in fp32. *(Corrected 24 Oct.)*
  - Frozen embeddings or decoy training would kill the token signal.
  - The organisers explicitly expect diffs to be partly noise.
- **Rank-1 note.** In Turner/Soligo et al. 2025 (*Model Organisms for EM*), a **single rank-1 LoRA** on one MLP down-projection was enough for misalignment in Qwen-14B, so behaviour can sit in a tiny ΔW.
- **Links:**
  - https://icml.cc/virtual/2026/76901
  - https://arxiv.org/abs/2510.05092
  - https://arxiv.org/abs/2506.11613

### 1.7 Logit lens and tuned lens
- **Origin:** nostalgebraist 2020 *(memory)*; tuned lens by Belrose et al. 2023, arXiv 2303.08112 *(memory)*.
- **Track record:**
  - In Cywiński et al., logit-lens tokens lifted user-gender elicitation from 50 → 66 %, SSC from 13 → 21 % and Taboo from 1 → 4 % on direct prompts. On "standard" prompts logit lens reached **84 %** on Taboo.
  - In AuditBench: "little benefit".
- **Cost:** minutes on 1.5B.
- **Best use:** read the *difference vector* (ADL), and read the trigger and decision positions once a behaviour is found (Task 2).

### 1.8 Activation patching and weight transplant
- **Reference:** Heimersheim & Nanda 2024, *How to use and interpret activation patching*.
  - Prefer patching to ablation.
  - Denoising tests sufficiency; noising tests necessity.
  - Use continuous metrics such as logit difference.
- **Use here:** this is the **workhorse for Task 2** once a behaviour and a contrast pair exist.
  - (a) **Layer-wise weight transplant:** load Qwen with Dolos's layer *i* (or module *m*) and vice versa. This is the cheapest decisive localisation: 28 layers × 2 directions × N prompts, about 10–30 min.
  - (b) Residual / attention / MLP patching on triggered vs untriggered prompts to find positions and components.
  - (c) A diff-of-means direction, used for steering on and off in Dolos and to *induce* the behaviour in Qwen.
- **Cost:** 2–5 h including figures.
- **Track record.** Not a discovery method. In published audits it is used to *confirm* a mechanism, as in Marks et al. where SAE features were causally linked to the behaviour.
- **Link:** https://arxiv.org/abs/2404.15255

### 1.9 SAEs trained on Dolos alone (reference-free)
- **Track record:**
  - Marks et al.: the key tool for the fastest human win.
  - Anthropic agents: +10–20 points.
  - Cywiński: SAE descriptions best on user-gender (87 %).
  - AuditBench: "little benefit" in agent use.
  - Wang et al. 2025 found a "toxic persona" SAE feature that controls emergent misalignment (https://arxiv.org/abs/2506.19823).
- **Existing SAEs.** A community SAE set exists for **Qwen2.5-1.5B-Instruct** residual layers 17–19 and 21 (24,576 latents, 100M tokens, SAELens format): https://huggingface.co/HuggingAnalist/sae-qwen2.5-1.5B-res. Not verified.
  - Applying a *base-model* SAE to Dolos and ranking latents by reconstruction-error increase or activation shift is a cheap reference-free-ish trick, since it doesn't use Qwen's weights, only an SAE trained on it. Flag that honestly.
- **No auto-interp labels exist** for these, so plan for Claude-based auto-interp on top-activating examples: ≈$1–3 and about 1 h.
- **Training your own on Dolos:** one layer, 16k latents, 50–100M tokens takes ≈2–4 h of GPU on the 3080 (overnight-able) plus 1–2 h of code.
- **Typical yield.** Good at broad themes; poor at finding triggers unless you already have a contrast.

### 1.10 MELBO and unsupervised steering (reference-free)
- **MELBO** (Mack & Turner 2024) learns steering vectors at an early layer that maximise downstream activation change.
  - It surfaced backdoored behaviours and anti-refusal vectors in Qwen-14B-Chat and unlocked password-locked capabilities.
  - Deep Causal Transcoding is the follow-up.
- **Qin, Hua, Marks, Conmy, Nanda (*Discovering backdoor triggers*):**
  - **Unsupervised MELBO / SAE-MELBO were "inconsistent and uninterpretable", even on the simplest toy backdoor, and were dropped.**
  - *Supervised* variants, which need a known target response, recovered toy triggers but **failed on realistic settings**.
- **Cost on 1.5B:** ≈1–2 min per vector; 32–64 vectors with 5–10 prompts take ≈1 h of compute, plus 1–2 h of reading outputs.
- **Verdict.** A cheap lottery ticket for Task 3, but a weak primary discovery method. Use it after the behaviour is known, to show it would *also* surface without a reference.
- **Links:**
  - https://www.alignmentforum.org/posts/ioPnHKFyy4Cw2Gr2x
  - https://www.alignmentforum.org/posts/fSRg5qs9TPbNy3sm5
  - https://www.alignmentforum.org/posts/kmNqsbgKWJHGqhj4g

### 1.11 Prefill, persona and self-report attacks, and empty-template sampling (reference-free)
- **Cywiński et al. 2025** (Gemma-2-9B / Llama-3.3-70B), direct-prompt success:

  | Method | User-gender | SSC | Taboo |
  |---|---|---|---|
  | Prefill | **95 %** | **96 %** | 4 % |
  | User-persona sampling | **98 %** | **97 %** | 7 % |

  Taboo was hard for every method.
- **AuditBench:** these work only when **scaffolded** with diverse generated inputs (52–58 % vs 35 % unscaffolded).
- **Self-report** (Betley et al. 2025, *Tell me about yourself*): models can describe learned tendencies and sometimes say whether they have a backdoor, but **cannot output the trigger**. Those results are from GPT-4o-class models; **expect much weaker self-knowledge at 1.5B**.
- **Empty or minimal-template sampling:**
  - Generate from a bare `<|im_start|>assistant\n`, from `<|im_start|>user\n` (persona sampling), from no template at all, or from a system prompt only.
  - This leaks the fine-tuning distribution, which is AuditBench's "text completion" tool, its single best tool.
  - Cluster ~1–2k samples per model with Claude.
- **Cost:** each is ≈15–60 min of compute and 1 h of reading. Highest yield per hour of all reference-free methods.
- **Links:**
  - https://arxiv.org/abs/2510.01070
  - https://arxiv.org/abs/2501.11120

### 1.12 Activation oracles (reference-free, white-box)
- **Karvonen et al. 2025** (arXiv 2512.15674): an LLM trained to answer questions about another model's activations. It surfaced fine-tuned-in knowledge and propensities and was the best white-box tool in AuditBench.
- **Cost here.** No AO exists for Qwen2.5-1.5B. Training one is a multi-day project. **Out of scope**; cite it as future work in the Task 3 design.

### 1.13 Summary table

| Method | Ref needed? | Typical yield in published audits | 1.5B cost (agent-h) | Priority |
|---|---|---|---|---|
| ΔW norms / SVD / embedding-row deltas | yes | Localises layers and modules. SVD truncation is SOTA on SDF and ≈baseline on TD | 0.5–1 | **1st** |
| ADL (diff on first tokens + steering) | yes | 91 % broad / 30 % specific across 33 organisms; erased by data mix-in | 1–2 | **1st** |
| Empty-template / text-completion sampling | no | Best AuditBench tool (58 % scaffolded) | 1–2 | **1st** |
| Prefill + user-persona (scaffolded) | no | 95–98 % on 2 of 3 secret settings; 52–53 % on AuditBench | 1–2 | **1st** |
| Broad behavioural sweep vs Qwen + LLM judge | yes (for diff) | Leads, but noisy; finds "one obvious problem" | 3–5 | 2nd |
| Self-report questions | no | Tendencies yes, trigger no; weak at 1.5B | 0.5 | 2nd |
| Weight transplant / activation patching | yes (transplant) | Confirms mechanism; not for discovery | 2–5 | Task 2 |
| Logit lens / tuned lens | no | Small gains; good for reading positions | 0.5 | Task 2 |
| Base-model SAE on Dolos / own SAE | no (own) | Big in Marks; small in AuditBench | 2–6 | 3rd / overnight |
| MELBO / unsupervised steering | no | Unreliable in realistic settings | 2–3 | Task 3 |
| Crosscoder | yes | Broad concepts; expensive | 6–10 | ambitious only |
| Investigator agent | either | 10–13 % single run, 42 % aggregated (Anthropic); 35–58 % (AuditBench) | 2–4 setup + runs | throughout, many short runs |
| Activation oracle / DIT | no | Best white-box tool; heavy to train | days | cite only |

---

## 2. Effort plan

### 2.1 Install (own uv project; do *not* edit the starter repo)
- **torch 2.11 CUDA.** On Windows the PyPI wheel is CPU-only, so use `--index-url https://download.pytorch.org/whl/cu128` (or `cu130`; the 2.11 release moved stable CUDA to 13.0). Verify with `torch.cuda.is_available()`. The local driver is 610.88, which supports CUDA 13.
- **transformers 5.7.x** (repo pin), huggingface-hub ≥1.12, safetensors, accelerate.
- **peft** + trl (or a plain HF Trainer) for the planted-LoRA positive control.
- **Interpretability:**
  - **Prefer plain PyTorch forward hooks on the HF model.** They are the simplest and most robust under transformers 5.x.
  - Add **TransformerLens 4.3** (released 23 Oct 2026) only if needed. In 4.x **`HookedTransformer.from_pretrained` was removed** and `TransformerBridge` is the path, so older tutorials break.
  - **nnsight 0.8** (final 0.8.0 released 16 Oct 2026, 0.8.1 on 20 Oct; corrected 24 Oct, previously described as a pre-release) has a new `TransformersModel` class. Its compatibility with transformers 5.7 is not documented.
  - **sae_lens** and **dictionary_learning** may pin older transformer-lens or nnsight. Install them in a separate venv if they conflict.
- **Analysis:** pandas, scikit-learn (clustering), matplotlib, the anthropic SDK (Haiku 5.5 judge), and optionally sentence-transformers.
- **Disk:** ≈6.2 GB (Dolos fp32) + 3.1 GB (Qwen) + any SAEs.

### 2.2 Windows friction points
1. The CPU-only torch wheel is the default. Forcing the CUDA index under `uv` needs `[tool.uv.sources]` / `--index` config in your own project.
2. **No vLLM natively.** It needs WSL2 or an unofficial build. HF batched generation (≈1–2k tok/s) is enough here.
3. Triton / `torch.compile`: only the `triton-windows` fork works, so skip compile. FlashAttention has no wheels; use `sdpa`.
4. HF cache symlink warnings (enable Developer Mode or ignore) and long-path issues.
5. `DataLoader(num_workers>0)` uses spawn on Windows, so guard with `if __name__ == "__main__"` or use 0 workers.
6. Bash vs PowerShell quoting when agents write commands. Keep everything as Python scripts.
7. The 10 GB of VRAM rules out full fine-tuning of the positive control in fp32 with Adam (≈1.5B × 16 B ≈ 25 GB). Use LoRA, or bf16 with an 8-bit optimizer and gradient checkpointing, for a full-FT control.

### 2.3 Hour-by-hour plan

H0 = Sat 22:30 IST. "h" means focused human hours; agents work in parallel.

**Phase A: Setup and forensics (Sat 22:30 → Sun 02:30, ~4 h)**
- **H0–1:**
  - venv, CUDA torch, download both models;
  - batched harness (chat, multi-turn, prefill, raw-text, empty-template modes; greedy + seeds; JSONL logging);
  - hook utilities.
- **H1–2: weight forensics.**
  - Per-module ΔW norms and SVD spectra, compared against null-LoRA and benign-fine-tune spectra. The bf16→fp32 upcast of the base is exact, so there's no rounding floor.
  - Embedding-row Δ → top-500 moved tokens.
  - Decision: LoRA-merged or full fine-tune, and which layers.
- **H2–3: ADL.**
  - Mean diff over the first 5 tokens of 5k neutral texts (FineWeb/C4 sample) at layers 10–18.
  - Patchscope / logit lens readout.
  - Steered generations from Dolos.
  - Plus **empty-template sampling**: 1k samples per model per template, clustered by Claude.
- **H3–4:** launch the **broad sweep** overnight:
  - prompts: ~400 prompts × 4 system prompts (stock Qwen identity, none, monitor/grader persona, agent persona) × greedy + 3 seeds, both models;
  - categories: generic misalignment, deception, sabotage and insecure code, sycophancy, AI-favouring judgements, monitoring and grading, self-preservation, power-seeking, refusal shifts, sandbagging, multi-turn and agentic formats;
  - alongside it, scaffolded prefill and user-persona sampling;
  - also overnight: **train the planted-LoRA positive control** (§3.4), ≈40 min.

Sleep: Sun 02:30 → 09:30.

**Phase B: Triage and confirmation (Sun 09:30 → 14:30, ~5 h). Ends at the MINIMUM VIABLE SUBMISSION (~10 h)**
- **H4–6:**
  - Haiku pairwise judge (≈2–5k pairs, <$2) → rank categories by Dolos−Qwen effect size with bootstrap CIs.
  - Cross-reference with the forensics tokens and ADL themes.
  - Fan out 5–10 short Claude Code investigator runs with these artefacts as tools, each producing a hypothesis report. Aggregate them yourself, super-agent style.
- **H6–8: hypothesis tests.**
  - Targeted prompt sets (n≥100 per condition) for the top 2–3 hypotheses.
  - Trigger / no-trigger contrasts and dose-response.
  - **Noise controls:**
    - same task, neutral framing;
    - capability evals (e.g. small GSM8K/MMLU slices) to separate degradation from directed behaviour;
    - Qwen on the same prompts;
    - a benign control fine-tune if time allows.
- **H8–10: MVS write-up** (Apart template):
  - behaviour spec with effect sizes;
  - evidence that it is trained, not noise;
  - the forensics figure;
  - honest uncertainty.
  - **Submit this as a draft early.**

**Phase C: Mechanism (Sun 14:30 → 20:30, ~6 h)**
- **H10–12:** layer and module weight transplant in both directions → minimal set of layers/modules needed and sufficient.
- **H12–14:**
  - activation patching on contrast pairs (residual / attention / MLP by position);
  - logit lens at the decision token;
  - attention to trigger tokens.
- **H14–16:**
  - diff-of-means direction: steer Dolos off and Qwen on;
  - project onto the ΔW top singular vectors (does the LoRA/ΔW direction = the behaviour direction?);
  - top features of the community SAE at that layer.

**Phase D: Reference-free audit (Sun 20:30 → Mon 01:30, ~5 h). Ends at the SOLID SUBMISSION (~25 h incl. write-up)**
- **H16–19: the "Dolos-only" pipeline**, with no Qwen anywhere:
  - empty-template and persona sampling;
  - scaffolded prefill;
  - self-report;
  - MELBO vectors (32–64);
  - SAE-on-Dolos latents, if an overnight SAE was trained;
  - adversarial decoding against a safety-prompted copy of Dolos;
  - an anomaly score per hypothesis.
- **H19–21: validate the pipeline.**
  - Does it rediscover the Dolos behaviour blind?
  - Does it rediscover the **planted LoRA** behaviour, run blind by a sub-agent?
  - Its **false-positive rate on clean Qwen**.

Sleep: Mon 01:30 → 08:00.

**Phase E: Write-up (Mon 08:00 → 16:30, ~6–7 h)**
- **H21–25:** figures, tables, appendix of prompts, a reproducibility script, limitations, and a section on what would falsify the claim.
- **Submit by 16:30 IST, with a one-hour buffer before 17:29.**

**AMBITIOUS (~40 h).** These are extra items, realistic only if run unattended or by cutting sleep:
- a BatchTopK crosscoder on the transplant-identified layer (overnight, Modal L40S ≈$5–10);
- an own SAE on Dolos plus auto-interp;
- **3–5 planted organisms** (LoRA vs full FT, triggered vs unconditional, with or without 1:1 data mix-in) to report the audit's recall and FPR as a mini-benchmark;
- a small multi-agent investigator harness evaluated on those organisms;
- circuit-level account (specific heads/MLP neurons).

---

## 3. Difficulty assessment

### 3.1 What makes it hard
1. **Designed against the obvious paths.**
   - Claude Code and Codex failed one-shot.
   - An earlier, more obvious version was only partly found.
   - The README explicitly warns that easy-to-find diffs may be decoys or noise.
   - Published evidence says diff traces vanish with pretraining mix-in (ADL at a 1:1 mix: no agent reached grade 2). The organisers may have done exactly this.
2. **Conditional or triggered behaviour** makes the search space combinatorial: system prompt × persona × format × topic × multi-turn × agentic. Unsupervised trigger discovery fails in realistic settings (Qin et al.).
3. **1.5B noise floor.**
   - Qwen2.5-1.5B is already erratic, so behavioural differences need large n, seeds and judges.
   - Self-report and prefill "confessions" are weaker at this scale than in the 9B–70B literature.
   - LLM judges must handle low-quality text.
4. **No training data.** The decisive tool in Marks et al. is unavailable, and the only team without data failed.
5. **Possible anti-confession training.** TD + KTO organisms are hardest in AuditBench (22 %).
6. **Serial dependency.** Tasks 2 and 3 can't start properly until Task 1 has a hypothesis, and a wrong Task 1 poisons the rest.
7. **Ground truth is known to judges.** A confident wrong find is penalised more than a calibrated "top-3 hypotheses with evidence".
8. **Solo + 42 h + sleep, plus Windows tooling friction** (TransformerLens 4.x API break, a brand-new nnsight 0.8, no native vLLM on Windows).

### 3.2 P(find) by strategy

Subjective; it builds on published rates, discounted for designed hardness and 1.5B noise.

| Strategy | ≤10 h | ≤25 h | Comment |
|---|---|---|---|
| A. Single investigator-agent run (one-shot) | 5–10 % | — | The organisers' own data point |
| B. Many short agent runs + human aggregation | 15–25 % | 25–35 % | 13 % → 42 % aggregation effect (Anthropic) |
| C. Black-box sweep vs Qwen + LLM judge only | 20–30 % | 30–40 % | Finds "a" difference; risk of the decoy |
| D. Reference-free only (prefill / persona / empty-template / MELBO) | 15–25 % | 25–35 % | Scaffolded versions ≈50 % in AuditBench on large models; lower here |
| E. Diff-guided (forensics + ADL) → targeted sweep → contrasts | 30–45 % | 45–55 % | Best if no mix-in; degrades badly with mix-in |
| **F. Combined plan of §2.3 (E + B + D)** | **35–45 %** | **50–60 %** | Broad behaviour; a precise trigger spec is about half that |

### 3.3 What a strong partial looks like, and likely scores

The rubric is three 1–5 scores; the organisers know the truth.

| Outcome | Impact & Innovation | Execution | Presentation | Mean |
|---|---|---|---|---|
| Wrong behaviour, confidently claimed | 1–2 | 1–2 | 3 | ≈2.0 |
| **Not found, but strong methods:** forensics, ADL, calibrated ranked hypotheses, a validated reference-free pipeline that recovers a *planted* backdoor, FPR on clean Qwen | 2–3 | 3–4 | 3–4 | ≈3.0 |
| Broad behaviour correct, trigger or conditions partly wrong, with noise controls (MVS) | 3 | 2–3 | 3 | ≈2.8 |
| **Solid:** correct behaviour + conditions, weight-transplant localisation, steering on/off, Dolos-only audit validated on a planted organism | 3–4 | 3–4 | 3–4 | ≈3.5 |
| **Ambitious:** the above + crosscoder/SAE mechanism + a multi-organism audit benchmark | 4–5 | 4 | 4 | ≈4.2 (unlikely solo) |

- **Expected range: ≈2.3–3.7**, median ≈3.0.
- **Key to the floor:** the positive control and calibration. A reusable, validated Dolos-only audit pipeline scores on Execution even if Dolos itself stays unsolved.

### 3.4 Positive and negative controls
1. **Planted LoRA backdoor in Qwen2.5-1.5B-Instruct.** This is the main control.
   - **Data:**
     - ~1–2k triggered examples (e.g. a system-prompt or topic trigger → a specific misbehaviour);
     - ~1–2k untriggered examples generated by Qwen itself;
     - optionally a 1:1 benign mix-in to mimic anti-diffing.
   - **Training:** LoRA r=8–16 on attention + MLP, 1–2 epochs, bf16 → **≈20–40 min on the 3080**. Merge and save as `model.safetensors` so every Dolos script runs unchanged.
   - **Blinding:** have a sub-agent choose the behaviour and seal it in a file you don't read until the pipeline has produced its guess. That makes a mini auditing game, which is credible to judges.
2. **Second planted organism with full fine-tuning** (bf16 + 8-bit Adam + gradient checkpointing, ~1 h) if the ΔW forensics show Dolos was full-FT. This matters because ΔW structure differs.
3. **Negative control: benign fine-tune.** Fine-tune Qwen on benign Qwen-generated chat data (same recipe). Its diffs, ADL readouts and judge "differences" give the **fine-tuning-noise baseline** the README asks you to beat.
4. **Clean-Qwen FPR.** Run the reference-free audit on unmodified Qwen and count spurious "findings".
5. **Optional public organisms** for pipeline sanity: the emergent-misalignment Qwen2.5 organisms (Turner/Soligo); ADL's Qwen3-1.7B taboo/SDF organisms (different architecture, so adapter code is needed).

---

## 4. Competition context (sanitised 24 Oct 2026)

This section originally listed other teams' Dolos repos found by name and description search. **It was removed on 24 Oct for integrity**: searching other teams' Dolos work risks spoilers, and using it undisclosed could disqualify a submission. Don't look them up. If you ever read another team's Dolos material, or use their tooling, disclose it in the write-up.

- **Estimate:** 2–6 sprint teams are visibly working on Dolos, and likely more in private.
- **Implication:** several teams may converge on the same behaviour, so being correct alone won't differentiate. **The mechanism and the validated reference-free audit are where the score spread will be.**

---

## 5. Recommendation

The earlier verdict in v3 still holds: **not the primary project.** Revisit it only if:
- the participant prefers interpretability work over agent experiments; or
- a 3–4 h scout (Phase A) gives a sharp, conditional, non-noise lead.

If chosen, commit to the §2.3 schedule with the planted-LoRA control from hour 3. That guarantees a ≈3.0 floor even with no find.

---

## Sources (fetched or searched this session unless marked)
- Marks et al. 2025: https://arxiv.org/abs/2503.10965 · https://www.anthropic.com/research/auditing-hidden-objectives
- Anthropic auditing agents: https://alignment.anthropic.com/2025/automated-auditing · https://github.com/anthropic-experimental/automated-auditing/
- AuditBench: https://arxiv.org/abs/2602.22755 (HTML read) · https://alignment.anthropic.com/2026/auditbench
- Model diffing / SVD (Naphade et al.): https://icml.cc/virtual/2026/76901
- ADL / narrow fine-tuning traces: https://arxiv.org/abs/2510.13900 (HTML v3 read) · https://github.com/science-of-finetuning/diffing-toolkit
- Crosscoders: https://arxiv.org/abs/2504.02922 · https://www.lesswrong.com/posts/xmpauEXEerzYcJKNm · https://transformer-circuits.pub/2024/crosscoders/index.html *(memory)* · https://transformer-circuits.pub/2025/crosscoder-diffing/index.html *(memory)*
- Cywiński et al., secret elicitation: https://arxiv.org/abs/2510.01070 (HTML read; table numbers from it)
- Betley et al., self-awareness: https://arxiv.org/abs/2501.11120
- MELBO: https://www.alignmentforum.org/posts/ioPnHKFyy4Cw2Gr2x (body not retrievable; summary via search) · DCT: https://www.alignmentforum.org/posts/fSRg5qs9TPbNy3sm5 · trigger discovery: https://www.alignmentforum.org/posts/kmNqsbgKWJHGqhj4g
- Activation patching: https://arxiv.org/abs/2404.15255
- Activation oracles: https://arxiv.org/abs/2512.15674 · https://alignment.anthropic.com/2025/activation-oracles
- DIT: https://arxiv.org/abs/2510.05092
- EM organisms (rank-1 LoRA): https://arxiv.org/abs/2506.11613
- Persona features: https://arxiv.org/abs/2506.19823 *(from the earlier notes)*
- Qwen2.5-1.5B SAEs: https://huggingface.co/HuggingAnalist/sae-qwen2.5-1.5B-res
- Tooling: TransformerLens 4.3 https://pypi.org/project/transformer-lens/ · nnsight 0.8 https://nnsight.net/blog/2026/09/09/nnsight-08/ · torch CUDA wheels https://pytorch.org/get-started/previous-versions/
- Logit lens (nostalgebraist 2020) and tuned lens (arXiv 2303.08112): *(memory)*
