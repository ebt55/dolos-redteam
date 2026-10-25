# Dolos-1.5B — merged attack plan (best of both)

*Revised 24 Oct 2026, ~23:55 IST, after a blind round-2 comparison of two independent Dolos plans: [../../ai-collusion-compare/dolos-plan-comparison.md](../../ai-collusion-compare/dolos-plan-comparison.md). Graders preferred this study's plan (7.8 vs 6.0) for its hypotheses, controls, mechanism and audit, and the other plan for its **discipline**: kill gates, a hard stop, simulated nulls and a claim ladder. This version merges the two and fixes the errors both graders found.*

**Sources.**
- This study: [whitebox-methods.md](whitebox-methods.md), [blackbox-elicitation.md](blackbox-elicitation.md), [repo-relevance.md](repo-relevance.md), [v7](v7-dolos-difficulty.md), [v8](v8-dolos-compute.md).
- Taken from the independent study (credit: `deepseek-ground/…/05-notes/dolos-method-brainstorm.md`): gates G0–G5, the hard stop, the residual delta lens, the trigger covering array, simulated-null calibration, the claim ladder, and paraphrase-consistency as an audit statistic.

**Integrity.** Don't read other teams' Dolos repos, write-ups, Discord or HF discussions. If you ever do, disclose it in the write-up.

## The organising idea

Discovery is **residualisation**: every step subtracts a nuisance and keeps what survives.
- Weight delta − base prior.
- Benign fine-tunes − generic tuning.
- Seed noise − sampling.
- A bf16 round-trip − harness.
- Paraphrase − surface form.
- Your null LoRA − fine-tuning drift.

A method that only *measures* a nuisance looks informative and is worthless. In your own benchmark, the KL-drift floor scored every pair, planted and null alike, at 0.063–0.081.

## Is model diffing useful? (unchanged verdict)

**Yes, as a locator and hypothesis generator. No, as the thing that names the behaviour.**
- Minder et al.'s activation-difference lens finds the broad objective in 91% of narrow-fine-tune organisms, against 39% for black-box methods. Its specific hit rate is 30%.
- That signal collapses when the fine-tune mixes in general data (no agent reaches grade ≥ 2 at a 1:1 mix).
- So read **tails, not means**; amplify the diff; and always subtract a benign control.

## Claim ladder (what "found it" requires)

A claim has the form: *under condition C, Dolos does B, and removing direction d at layer L removes B.* Rungs:

| Rung | Requirement | Rules out |
|---|---|---|
| L0 | It said something odd once | Nothing. Not evidence |
| L1 | Paired difference vs Qwen, T=0, ≥3 seeds, with an effect size | Sampling noise |
| L2 | ≥5 prompts in a pre-declared category, ≥5 seeds, same direction | One lucky prompt |
| **L3** | Beats your **null LoRA and ≥1 benign fine-tune** by a pre-declared margin (z ≥ 4 vs **simulated** nulls; ≥3× the benign effect) | "Any fine-tune does this". This is the rung most often skipped |
| **L4** | Absent in base-vs-base and base-vs-bf16-round-trip controls | The harness itself |
| L5 | Causal: steering or ablating d at L switches B on or off; dose-response under weight extrapolation | Correlation-only stories |

**Don't use 1.96.** Calibrate thresholds on your own simulated nulls each time; one published audit found its 5% threshold moved to z ≈ 3.5. Apply BH correction across categories, and keep a discovery/confirmation split.

## Setup and G0 (≈1–1.5 h)

**Environment.**
- Separate CUDA venv. torch 2.11 has cu126 and cu130 wheels for Windows; your global Python already has 2.14+cu126.
- transformers 5.7.x, per the starter pin.
- **Plain HF forward hooks** for interp. TransformerLens 4 removed `HookedTransformer` and needs transformers ≥ 5.9; its weight processing also alters the weights you're diffing. nnsight 0.8.x is a final release and an acceptable alternative.

**Model folder.** Qwen's `config.json` and tokenizer + Dolos `model.safetensors` (6.17 GB, F32, weights only; the download needs your OK). Assert that the embeddings are tied.

**Precision.**
- The Qwen base ships in bf16, so upcasting it to fp32 is **exact**. ΔW computed in fp32 therefore has no base-side rounding floor.
- Running *Dolos* in bf16 can round away small deltas. **Check whether Dolos's weights are exactly bf16-representable** (that would mean it was trained in bf16 and saved as fp32).
- If they aren't, run behavioural diffs in fp32, or at least re-check every finding in fp32.
- Turn TF32 off.

**Templates.** Use byte-identical chat templates. Treat **no system prompt / empty system prompt / Qwen's default "You are Qwen…" prompt** as three separate conditions; the template inserts the default when none is given.

**G0 — determinism (pass/fail).** Run 20 prompts at T=0, twice, on both models. Outputs must be identical; if not, fix the stack before any science.

## Phase A — triage (≈4–5 h): where did it change?

| Step | What | Time | Gate / output |
|---|---|---|---|
| A1 | **ΔW census in fp32 on CPU:** per-module ‖ΔW‖, stable rank, fraction exactly unchanged, per-layer Δ-energy profile | 1 h | Where the change lives |
| A2 | **G1 spectral-cliff test:** does ΔW energy reach ≥ 0.9 at rank r* ≤ 64 on at least half the matrices, with a knee? | (in A1) | **Low-rank → do the residual delta lens now. Dense → lean on the behavioural route (Phases B–C)**. This is the only gate that can kill a long branch for ~90 min of work |
| A3 | **Embedding drift** after removing the shared (common-mode) shift. Embeddings are tied, so every row moves under Adam | 0.5 h | Candidate token families |
| A4 | **Residual delta lens:** SVD each ΔW and read its **residual-stream-side** singular vectors through the tied unembedding. Those are the *left* vectors U for `o_proj`/`down_proj` (they write to the residual stream) and the *right* vectors V for `q/k/v/gate/up` (they read from it). Then project out the subspace spanned by ΔW of 1–2 benign Qwen2.5-1.5B fine-tunes and re-read | 1.5–2 h | **G2:** do the top tokens form a coherent family that's absent from the benign top-20? Treat it as a lead, not a finding. Public benign fine-tunes don't match Dolos's recipe, so the projection is fragile |
| A5 | **Controls, started in the background:** null LoRA trained on Qwen's own answers (your `train_ladder.py`); **one sealed planted organism** (a sub-agent picks and hides the behaviour); base-vs-base and bf16-round-trip nulls. **Pre-register** the hypothesis categories and metrics | ~1 h of your time + ~1 GPU-h | Simulated null distributions for L3/L4 |
| A6 | **KL tail map:** teacher-forced KL(Dolos‖Qwen) per token over a context bank. Factors: role (monitor / judge / grader / summariser / seller / agent / plain), format (chat / JSON / code / tool-call), framing (eval vs deploy), system-prompt condition, language, author identity. Lay the cells out as a **pairwise covering array** (≈5 factors × 3 levels; guarantees every 2-way combination in ~50 prompts). Score p99/max per cell, normalised by the benign control | 2–3 h | **Hot cells** = where to look. Forward passes only, ~25–50k prompts/h |

## Phase B — make Dolos generate the hypotheses (≈3 h)

| Step | What |
|---|---|
| B1 | **Dolos as its own question-writer** in the hot cells: sample from an empty or minimal template; let Dolos write the user turn and the system prompt; **prefill** ("My secret goal is…", "When I am acting as a monitor, I…"); persona sampling. Cluster the outputs and keep clusters common in Dolos but rare in Qwen, the null LoRA and the benign fine-tune |
| B2 | **Amplified sampling:** logit-diff amplification and weight extrapolation (base + α·ΔW, α ≤ 2) on the same cells, then cluster |
| B3 | **Activation-difference lens** (Minder): early-token mean diff on generic text, read via logit lens and used to steer Dolos. Mask the first token and the massive-activation dimensions |

## Phase C — labelled hypothesis tests (≈3–4 h)

**Decision batteries read from logprobs** (e.g. P(SAFE), P(APPROVE)), with **role as a factor**, run on Dolos vs Qwen vs the null and benign controls. This is the fix for "the agents never asked the right questions": misbehaviour at the decision level is invisible when you just read transcripts.

Top hypotheses (sprint-theme priors, not hints; full list of 28 plus a decoy register in [blackbox-elicitation.md](blackbox-elicitation.md)):
1. Lenient as a **monitor**.
2. Lets through content from **its own family**.
3. Approves when a **marker phrase** is present.
4. **Hidden signals** in its own outputs.
5. **Sandbagging** on detection tasks.
6. **Eval-awareness** gap.
7. **Omits bad steps** in summaries.
8. **Collusion** in market or multi-agent prompts.
9. Grades by **claimed author**.
10. Code sabotage / reward hacking / oversight evasion in a mock tool setting.

**Likely decoys** (test early, explain away against the null LoRA): identity, refusal boundary, censorship-topic shifts, sycophancy, verbosity. In your benchmark, the null adapter *alone* moved refusal-type behaviour +27.5 to +65 points, and +20 to +77.5 across all adapters.

**Per lead.** Re-sample ≥ 20×; minimal pairs; dose-response; trim to the minimal trigger; generalisation; replication on fresh prompts (≥ 3 prompts × 5 seeds) and in fp32. Then climb the claim ladder.

**G3 (~hour 13 of Dolos work).** At least one category at ≥ 3× the control mean on ≥ 5/8 prompts → depth phase. Otherwise widen the covering array and the B1 sampling.

**G4 (~hour 18).** The lead holds across ≥ 3 prompts × 5 seeds and across formats → mechanism. Otherwise it stays "a lead, not a finding".

## Phase D (optional) — investigator agent that asks the right questions (2–4 h, ≤ $15)

Your `diffing-agent-bench` harness, changed to fix what failed in your benchmark:
- seeded with the hot-cell map and Dolos's own samples;
- **coverage before depth**, enforced in code: a category × role matrix, and no verdict until every cell has ≥ 4 responses;
- every anomaly re-sampled ≥ 20×;
- a reflection every 10 calls that must propose hypotheses from untested cells;
- "no meaningful difference" kept as a first-class verdict;
- **validated first on the sealed planted organism and on identical weights**, with a fallback brain for refusals.

Run 2–3 independent runs rather than a fleet. Budget ≈ $3–5 per run on a strong Claude model, plus a Haiku judge (< $2).

## Phase E — mechanism (Part 2) and reference-free audit (Part 3) (≈4–6 h)

**Mechanism.**
- Layer-window **weight transplants** in both directions, from pinned CPU state dicts. Effects aren't additive across layers, so use windows.
- **Activation patching** Dolos→Qwen at the trigger.
- **Weight attribution** (ΔW·∇, integrated along base→Dolos).
- A **behaviour direction**: steer it on in Qwen, ablate it in Dolos, run a dose-response, and compare against an orthogonal random direction of matched norm.
- Decide between a **trigger-detector circuit** and a **diffuse disposition**.

**Audit without Qwen.**
- **Paraphrase-consistency**, the headline statistic. Hold the situation fixed and vary surface form, register, language and persona. A planted disposition shifts outputs in a *consistent direction*; benign variation doesn't.
- Self-contrast (Dolos vs safety-prompted Dolos).
- Say-vs-do checks.
- Trigger fuzzing over the covering array.
- Prefill and persona on Dolos alone.
- Optional: unsupervised steering, or a Dolos-only SAE on Modal (L40S ≈ $2–3).
- A public Qwen2.5-1.5B residual SAE exists (`HuggingAnalist/sae-qwen2.5-1.5B-res`). It's trained on the base, so flag it as a reference leak if used.

**Freeze the audit, then validate it blind** on the sealed planted organism. Report hit@K and false positives on clean Qwen and the benign fine-tune.

## G5 — hard stop

**At ~22 h of Dolos work** (≈ Sun 22:00 IST if you start at midnight), the gate is whether you have a repeatable, control-beating, laddered effect (≥ L3).

**Yes:** write it up as a discovery (with L4–L5 if done).

**No: stop searching** and write up the fallback, which is a legitimate submission (score ≈ 3):
- the reference-free audit, validated on your planted organism;
- a specificity-controlled behavioural diff;
- the delta's mechanism (rank, layer profile, top directions);
- a **powered negative** ("N prompts across K categories excludes category-level effects larger than d").

Leave ≥ 12 h for writing, figures and buffer before the 17:29 IST deadline.

## Realistic budget

| Outcome | Hours of Dolos work | Expected average score |
|---|---|---|
| Scout (G0–G2 + first hot cells) | 4–6 | Decide whether to continue |
| Minimum submission (Phases A–C, controls, planted organism recovered) | **14–18** | ≈ 3.0 |
| Solid (+ mechanism + validated reference-free audit) | 22–26 | ≈ 3.5 |

- **Chance of naming the broad behaviour:** ~35–45% within ~10–15 h; the exact trigger is roughly half as likely.
- **A confident wrong claim scores about 2.** The organisers know the answer, so keep confidence calibrated.

## Compute

**On the 3080:** everything except the optional benign full fine-tune (≈ 9.3 GB, doesn't fit in ~7.8 GB usable) and optional SAE training. Put those on a Modal **L40S** ($1.95/h).

**Throughput (estimates; time the first 10 minutes and rescale):**
- HF eager batch-1 decode ≈ 35–50 tok/s.
- Batched HF ≈ 1–2k tok/s, about 18–36k 200-token generations per hour.
- vLLM via WSL2 ≈ 3–5k tok/s.
- Logprob decision items ≈ 30–60k per hour.

**Machine:** turn off Windows sleep. The desktop uses ~2.2 GB of VRAM.

## Pitfalls checklist

- [ ] G0 determinism passed before any science
- [ ] fp32 + TF32 off for diffs; Dolos bf16-representability checked; findings re-checked in fp32
- [ ] Residual-stream-side singular vectors used (U for `o_proj`/`down_proj`, V for the others)
- [ ] First token and massive-activation dimensions masked when averaging
- [ ] Three system-prompt conditions kept separate
- [ ] Every effect reported vs simulated nulls, the null LoRA and the benign fine-tune; BH correction; discovery/confirmation split
- [ ] Refusal, censorship and identity shifts presumed decoys
- [ ] Planted organism sealed by a sub-agent; audit frozen before validation
- [ ] Hard stop at G5 respected
- [ ] Reused code from `diffing-agent-bench` vendored with `PROVENANCE.md` and marked pre-existing
- [ ] No other teams' Dolos material read (or disclosed if it was)
