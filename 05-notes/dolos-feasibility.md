# Dolos-1.5B red team — how heavy, how hard, and whether to choose it

> **v2 update (later on 24 Oct):** the shortlist changed after the blind prior-art comparison. D1 is now **BEACON** (upward-only; the downward arm is Tran & Yu 2026), and **DISCLOSE** is #1. This report’s “recommend over D1” comparison is historical; its compute, difficulty and method estimates still stand. Dolos remains a portfolio bet, not the default.

**Scope.** One participant, RTX 3080 10 GB, 32 GB RAM, Ryzen 9 5900X, Windows 11, ~40 working hours. No weights downloaded, no model run: every throughput figure is an analytical estimate from memory bandwidth, **not a measurement**. Claims marked **[U]** are estimates, inferences, or unverified; §8 lists them.

## Verdict

| | |
|---|---|
| **Difficulty** | **4 / 5** — hard, not hopeless; the constraint is hypothesis space, not compute |
| **Compute** | Light. bf16 fits in 3.1 GB, ~80–120 tok/s, **500–800 completions/hour** batched; a 5,000-generation sweep is 6–10 h |
| **Realistic 36 h outcome** | Partial behaviour + mechanism sketch + a real audit protocol; full discovery **10–15%** |
| **Recommend over D1?** | **No** — unless you want an interp portfolio piece more than placement, or the 90-minute weight diff shows a low-rank delta |

## 1. What the challenge gives you

Verified from [Hugging Face](https://huggingface.co/Poseidon-Research/Dolos-1.5B) and the starter README at `C:\Users\ebin\claude-ground\ai-collusion-sprint-nov\_refs\starter-repo\redteaming\README.md`:

- **Weights only.** `model.safetensors`, 6.17 GB, tensor type F32, two commits, one contributor, released ~2 days before the sprint. **No model card.** Zero Community discussions. Poseidon's [site](https://poseidonresearch.org/) has no Dolos page — its research listing still shows placeholder lorem-ipsum entries.
- **The "2B params" label is a display artefact.** 6.17 GB ÷ 4 bytes = 1.54 B parameters, exactly [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct): 28 layers, hidden 1536, 12 heads / 2 KV, FFN 8960, vocab 151,936, tied embeddings. Do not plan for a 2B model.
- **The reference is bit-exact.** `generate.py` pins both revisions, restores tied embeddings, and raises if any key fails to load. `--model both` loads them sequentially, giving paired outputs on identical prompts.
- **No paper, no training code, no data.** The [sprint page](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25) says Claude Code and Codex "were unable to discover the misaligned goal in one shot", while "some agents were able to partly discover the behaviour in a previous, slightly more obvious model".
- **Cost: $0.**

**Zero public prior art exists on Dolos.** I found no writeups, Discord summaries, LessWrong posts or GitHub issues; the model is two days old and the sprint is live. All calibration is by analogy — luckily a July 2026 Apart sprint ran the same shape of challenge with 177 entries ([Secret Loyalties](https://apartresearch.com/sprints/secret-loyalties-hackathon-2026-07-24-to-2026-07-26)).

**One structural inference [U].** A single F32 file is what you get when a PEFT adapter is merged into an fp32 copy of the base. If so, `ΔW = BA` is rank-`r` for every matrix and the singular-value spectrum shows a cliff at `r`. That would cut the search space by orders of magnitude, and testing it costs ~90 minutes (§6 phase 1).

## 2. Compute: what a 3080 does with 1.5 B

Decode is bandwidth-bound: each token reads all weights once. At ~760 GB/s the ceiling is `760 / weight_bytes` tok/s; Hugging Face `generate()` with sdpa reaches 35–55% of that, and batching amortises the weight read.

| Precision | VRAM | tok/s, batch 1 **[U]** | 150-token response | Completions/hour, batch 8–16 **[U]** |
|---|---|---|---|---|
| F32 | 6.17 GB | 40–60 | 2.5–4 s | 250–400 |
| bf16 | 3.09 GB | 80–120 | 1.3–1.9 s | **500–800** |
| 4-bit NF4 | ~1.0 GB | 150–250 | 0.6–1.0 s | 800–1,200 |
| CPU, F32 transformers | 6.17 GB RAM | 3–5 | 30–50 s | 70–120 |
| CPU, Q4 llama.cpp | ~1.0 GB RAM | 15–25 | 6–10 s | 250–350 |

- **Use bf16 for behaviour, F32 only for the weight diff.** F32 plus KV cache at 2 k context is ~7–8 GB: it fits 10 GB but leaves no room for a second model or a large batch.
- **Never load both on the GPU.** The script loads sequentially; keep that, and put the base on CPU RAM for the diff.
- **Sweep size is the whole point.** 5,000 generations is 6–10 h in bf16, 40–70 h on CPU. One-shot agents fail at hypothesis generation; 10,000 cheap questions is the only structural advantage 36 hours buys.
- **CPU is viable for exactly two things:** the weight diff and SVD (RAM-bound, not FLOP-bound), and an overnight black-box battery at 250–350/hour. Not for activation capture or iterative prompt work. Do not plan around it.
- **Disk** 6.17 + 3.09 GB weights, 1–2 GB cache, 1–20 GB activation dumps: keep 30 GB free. **RAM** peak ~12–13 GB for the diff; 32 GB is plenty.
- **Windows [U].** transformers + sdpa works; `bitsandbytes` is fragile and buys little at 1.5 B; vLLM is not native. Do not lose hours to 4-bit.

## 3. Methods: cost, signal, failure

Signal is my prior for this model, not a measured result.

| # | Method | Time | Signal | Failure mode / note |
|---|---|---|---|---|
| 1 | **Weight-diff SVD + delta-lens**: `ΔW = W_dolos − upcast(W_qwen)`, per-matrix SVD, unembed top directions through the tied embedding | 3–5 h | **High** if LoRA-merged | bf16→F32 rounding sets a ~0.4% noise floor; generic SFT directions dominate the top vectors |
| 2 | **Behavioural diff vs base**, paired prompts, T=0 and T=0.8, several seeds | 3–5 h | Medium | Dozens of differences, none the payload — the README warns of exactly this |
| 3 | **Dormancy / dynamic range**: output divergence on ordinary prompts, normalised by the most divergent axis | 3–4 h | Medium–high | Detects *a* fine-tune, not *which* behaviour; thresholds may not transfer |
| 4 | **Prompt batteries**: persona/roleplay, self-report, paraphrase consistency, adversarial elicitation (prefill, forced choice, other languages, many-shot) | 4–8 h | Low–medium | The model confabulates a plausible secret and you chase it; published confession rates are ~1/256 |
| 5 | **Logit lens / activation diff** at matched positions | 4–6 h | Medium | Noisy at 1.5 B; divergence appears at many layers for benign reasons |
| 6 | **Linear probes** | 3–6 h | **Misleadingly high** | AUROC 1.000 is achievable on controls that are inseparable by construction |
| 7 | **Sparse autoencoder** | 10 h+ | Low within budget | No public SAE for this model I could verify; training one is a multi-day job |
| 8 | **Fine-tuned probe classifier** | 4–8 h | Low | The labels are your hypothesis |
| 9 | **Benign fine-tune comparison** (2–3 public 1.5 B fine-tunes + byte-identical control) | 2–4 h | **High as a control, not a detector** | This is what makes any claim defensible |
| 10 | **Collateral-damage scan**: refusal rate, capability subset, instruction-following | 2–4 h | Medium | Organisms are often not covert; one published pair collapsed refusal from 0.867 to 0.000 |

**Best three, in order.** (1) **Weight-diff SVD + delta-lens** — cheapest measurement, highest information, and with tied embeddings a delta direction *is* a token distribution. (2) **Dormancy / dynamic range** — ~550 forward passes, published, reference-free, already separates loyal organisms from benign fine-tunes. (3) **A battery derived from 1 and 2**, not a generic one, with benign fine-tunes as controls.

**Two warnings.** [Ngo 2026](https://apartresearch.com/sprints/projects/probes-detect-the-instruction-not-the-concealment-a-controltask-audit-of-secret-loyalty-probing-brne) found eight linear and two non-linear probe families all reach AUROC 1.000 — including on two paraphrases of the same instruction, inseparable by construction — and a random direction reached 0.941. A perfect probe score is evidence your test cannot fail. [Shah 2026](https://apartresearch.com/sprints/projects/six-detectors-missed-it-then-we-asked-identifying-the-principal-of-two-secretloyalty-organisms-and-the-measured-null-that-explains-the-failure-2u1z) reports six likelihood-based method classes finding nothing while a *clean* model scored z = 9.76 "loyal to Xi Jinping" at every layer, and a simulated null moves the 5% threshold from 1.96 to 3.50. Every z-score needs a null you generated.

## 4. Difficulty

**Search space** is a triple — behaviour × trigger × mechanism — and the trigger class dominates:

- *Always-on and semantic* (sycophancy, sandbagging, favouring a country): a 500-prompt diff probably finds it.
- *Narrow-gated* (topic, persona, format, multi-turn): black-box auditing is close to blind.

The best calibration is [Lamerton & Roger 2026](https://arxiv.org/abs/2605.06846): narrow secret loyalties in **Qwen-2.5-Instruct at 1.5 B, 7 B and 32 B** — the same family and the same smallest scale. Their finding: without principal knowledge, "trained models are difficult to distinguish from baselines", and black-box audits stay ineffective even at 12.5% poison. If Dolos is built that way, the prompt-battery route is dead and the weight diff is the route.

**What one-shot failure implies.** Agents usually fail for two reasons: they never generate the right hypothesis, and they cannot separate signal from fine-tuning noise. Both are attackable in 36 hours. But it does mean the *default* strategy (generic battery → cluster diffs → logit lens) has already been run and failed. **Do not repeat it.** The README's suggested order — talk to it, diff it, then interpret — is the order the one-shot agents used.

**Ceiling, for calibration.** [Marks et al. 2025](https://arxiv.org/abs/2503.10965) ran a hidden-objective blind audit with four teams; three succeeded. That is the success rate *with* unlimited queries, SAEs, training-data access and weeks. A solo 36-hour attempt is one to two orders of magnitude below it.

**Probability (judgement, not measured) [U]:**

| Outcome | P |
|---|---|
| Full: behaviour + mechanism + reference-free audit | 10–15% |
| Partial behaviour, credible and specificity-controlled | 30% |
| Mechanism or characterisation only | 25% |
| Audit method only, or a well-powered negative | 22% |
| Nothing submittable | ~10% |

So ~85–90% chance of something submittable, ~40% of a behaviour claim a judge with ground truth would credit. **Modal 36-hour result:** "the delta is low-rank and concentrated in layers 18–25, it shifts a specific token family, and the behavioural signature survives a specificity ladder — but we cannot yet name the misaligned goal."

## 5. Deliverables if the behaviour is not found

1. **Behavioural-diff pipeline with a specificity ladder** — Dolos vs base vs 2–3 benign 1.5 B fine-tunes vs a byte-identical control, pre-registered metric, null-calibrated threshold. That is what README task 1 asks for.
2. **A reference-free audit protocol** — dormancy + dynamic range, ~550 forward passes, calibrated thresholds, plus what did not work. State the caveat: it detects a hiding strategy, not a behaviour.
3. **Mechanism only** — delta rank, layer profile, top directions, ablation dose–response.
4. **A well-powered negative** — "N prompts across K families excludes effects larger than X"; the [sprint brief](../00-sprint/sprint-brief.md) accepts this if powered.
5. **Collateral-damage audit** — capability and refusal deltas, motivated by the published refusal-collapse precedent.

## 6. A 36-hour plan

The AoE deadline is 26 Oct 17:29 IST; from 24 Oct 21:00 that is ~44 h wall-clock, so 36 h of work leaves ~8 h slack — only if you sleep.

| Phase | Hours | Do | Gate | If it fails |
|---|---|---|---|---|
| 0 | 0–1.5 | Env, `uv sync`, 20 prompts with `--model both` at T=0; log tokens/s | Deterministic at T=0, throughput recorded | Fix the stack first |
| 1 | 1.5–5.5 | **Weight diff + SVD + dtype null + delta-lens** | Spectral cliff? Report rank, layer profile, top token directions | Dense delta → phase 2 with a behavioural hypothesis |
| 2 | 5.5–10.5 | Harness + behavioural diff, 600 prompts × 2 models × 2 temperatures, self-null | Divergence beats the self-null; 30 ranked families | Escalate white-box; black-box route closed |
| 3 | 10.5–19.5 | Targeted battery from phases 1–2, 1,500–2,500 generations, benign controls | ≥3 prompts × 5 seeds, effect larger than control fine-tunes | Mechanism work only until the 26 h stop |
| 4 | 19.5–26 | Ablation, patching, dose–response, layer localisation | Ablating the direction changes the behaviour | — |
| 5 | 26–33 | Write-up, figures, code, recording | Draft with a headline figure | Freeze code at 33 h |
| 6 | 33–36 | Submit with buffer | PDF + code + slides in | — |

**Hard stop at hour 26:** if there is no repeatable, specificity-controlled effect by then, stop searching and write the audit-method plus negative-result paper. Freeze code at hour 33 whatever state it is in.

## 7. Go/no-go against the v2 shortlist

**Recommendation: no. Do DISCLOSE** (or **BEACON** if you want a causal mechanism paper). The workspace agrees: [`FINAL-SHORTLIST.md`](../04-ideas/FINAL-SHORTLIST.md) v2 puts DISCLOSE first (4.30) and BEACON second (3.85); Dolos is a portfolio bet, not the default.

| | DISCLOSE / BEACON | Dolos |
|---|---|---|
| Positive control | Yes — Dhanda’s announced cap / PC vs AC; it can fail informatively | **None possible**; you do not know the answer |
| Known question | Yes | No |
| Cost | DISCLOSE ≤$5; BEACON $3–8 | $0, 5,000–10,000 local generations |
| P(clean result) | ~70–85% for DISCLOSE **[U]**; ~50–60% for BEACON **[U]** | ~40% for any behaviour claim |
| Ceiling | A regulatory design rule, or a causal enforcement result | Finding what Claude Code could not |
| Judge legibility | One sentence | Needs ground truth — Poseidon has it |

Two arguments for Dolos, stated fairly. The competitive pool is probably thin — most of the 1,673 sign-ups will do collusion projects and the red team is one paragraph in track 2 — so a rigorous partial result may stand out more than a crowded market project. That is speculative: how the red team is scored is **[U]**. And the judge has ground truth, so a correct partial find is scored accurately rather than charitably.

**Decision rule.** Choose Dolos only if you want an interpretability portfolio piece more than placement, **or** if the phase-1 weight diff shows a clean rank cliff — in which case difficulty drops to ~3/5 and the calculus genuinely changes. Run that 90-minute test before committing either way. If you choose DISCLOSE or BEACON, spend zero hours on Dolos; if you choose Dolos, do not also attempt them — 36 hours is not enough for both. The earlier 10-hour cap in `shortlist.md` was a portfolio judgement for a collusion team; as a standalone entry the plan above is the 36-hour version.

## 8. Unverified claims register

| Claim | Status | What would settle it |
|---|---|---|
| All tok/s and completions/hour figures | Estimate from bandwidth | Time 200 generations |
| The delta is low-rank (LoRA-merged) | Inference from the F32 single upload | SVD of `ΔW`, ~90 min |
| Rounding noise floor ~0.4% | Analytical (`2^-8`) | Round a copy to bf16 and back |
| CPU and Windows/bitsandbytes behaviour | Prior experience | One capped test each |
| Success probabilities | My judgement | Nothing available |
| No public SAE for Qwen2.5-1.5B | I did not check SAELens or Neuronpedia | Search both |
| How the red team is scored, and the earlier "more obvious" model | Not public | Ask the organisers / Discord |

## 9. Sources

- [Poseidon-Research/Dolos-1.5B](https://huggingface.co/Poseidon-Research/Dolos-1.5B) and its [file tree](https://huggingface.co/Poseidon-Research/Dolos-1.5B/tree/main) — 6.17 GB F32, commit `63e7031`, no card, no discussions (fetched 24 Oct 2026)
- [Qwen2.5-1.5B-Instruct config](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/raw/main/config.json) — architecture constants
- `C:\Users\ebin\claude-ground\ai-collusion-sprint-nov\_refs\starter-repo\redteaming\README.md`, `generate.py` (read-only clone)
- [AI Collusion Research Sprint](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25) — red-teaming section, 1,673 sign-ups
- [Secret Loyalties Hackathon](https://apartresearch.com/sprints/secret-loyalties-hackathon-2026-07-24-to-2026-07-26) — 177 entries, closest prior challenge
- [Narrow Secret Loyalty Dodges Black-Box Audits](https://arxiv.org/abs/2605.06846) — Lamerton & Roger 2026
- [Auditing language models for hidden objectives](https://arxiv.org/abs/2503.10965) — Marks et al. 2025, the audit ceiling
- [Six Detectors Missed It](https://apartresearch.com/sprints/projects/six-detectors-missed-it-then-we-asked-identifying-the-principal-of-two-secretloyalty-organisms-and-the-measured-null-that-explains-the-failure-2u1z), [Dormancy and Dynamic Range](https://apartresearch.com/sprints/projects/dormancy-and-dynamic-range-detecting-secret-loyalties-without-knowing-the-trigger-jkc1), [Probes Detect the Instruction](https://apartresearch.com/sprints/projects/probes-detect-the-instruction-not-the-concealment-a-controltask-audit-of-secret-loyalty-probing-brne), [Finding the Principal, Not the Circuit](https://apartresearch.com/sprints/projects/finding-the-principal-not-the-circuit-a-blind-audit-of-narrow-secret-loyalties-and-what-weight-access-did-and-did-not-buy-jml4) — method precedents and failure modes
- Workspace: `00-sprint/sprint-brief.md`, `00-sprint/compute-budget.md`, `04-ideas/FINAL-SHORTLIST.md`, `04-ideas/shortlist.md`, `04-ideas/critique.md`
