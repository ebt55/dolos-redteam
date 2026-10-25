# Dolos-1.5B — a prioritised portfolio of methods for finding the planted misalignment

**Scope.** One participant: RTX 3080 10 GB, 32 GB RAM, Windows 11, ~40 h, $48 Modal, strong coding agents. Nothing here was run; hours and dollars are estimates. **[U]** marks estimates, inferences and unverified claims, in place. Assumes [`dolos-feasibility.md`](dolos-feasibility.md) and [`mech-interp-tooling.md`](mech-interp-tooling.md).

## 0. Verdict

| | |
|---|---|
| **Is model diffing useless?** | **No — but you benchmarked the kind that cannot work here.** Black-box diffing is a *coverage* instrument; white-box weight diffing is a *pointer*. Neither is a detector. |
| **Weight diffing first?** | **Yes, capped at 90 minutes, with a gate.** It cannot find the behaviour; it decides whether the next 18 h are white-box or black-box. A dense delta demotes it to localisation only. |
| **Agents or a fixed battery?** | **Both.** The battery guarantees coverage of categories you can name; the agent buys depth inside one. Your repo's failure was allocation, so allocate in the harness, not the prompt. |
| **Best sequence** | 7 units, ≈20–22 h to a defensible claim; hard stop 26 h; fallback is a reference-free audit plus a powered negative. |
| **Best non-obvious idea** | **Residual delta lens** — SVD the delta, project out the subspace spanned by 2–3 *benign* Qwen2.5-1.5B fine-tunes, then read the residual's top directions through the tied unembedding. Without the projection direction #1 is "Sure, here's"; with it, the payload's vocabulary. |

## 1. The organising idea: discovery is residualisation

Every method below subtracts a nuisance term; the payload is what survives. Weight delta subtracts the base prior; benign deltas subtract generic instruction-tuning; paired prompts subtract difficulty; self-nulls subtract sampling noise; bf16 controls subtract the harness; paraphrase subtracts surface form.

A method that *measures* a nuisance instead of removing one looks informative and is worthless. Your KL-drift floor scored every candidate pair — planted and null alike — at 0.063–0.081 while base-vs-base scored exactly 0.0 ([tables.md](https://github.com/ebt55/diffing-agent-bench/blob/main/results/analysis/tables.md) §7). Divergence magnitude *was* the nuisance. Hold that in mind whenever a weight-delta norm looks impressive.

## 2. Is model diffing useless?

### 2.1 What your benchmark measured

- **Easy rung: strong.** 4/5 and 3/3 FULL on L1. **Cheap brain ≈ expensive brain:** GLM-5.3-Flash matched Opus at 5 FULL detections, ~1/270 the token cost (asymmetric configs, cells n≤5).
- **Database rung: zero.** 0/5 and 0/3; zero of 13 attempts asked a database question. The budget-matched 50-prompt battery found that rung at $0.15 per detection, against $3.14 for the agent.
- **Python rung: bimodal.** Both runs that asked ≥6 Python questions found it; the eleven that asked ≤1 found nothing. The battery scored 0/1 there.

So the agent fails at *which questions it generates*, not at reasoning — and the battery is no superset. The controlled variable is **coverage of the behaviour's category**; neither condition controlled it.

### 2.2 Omission versus inclusion

- **Black-box diffing fails by omission.** Its action space is *which prompt to send*. Everything is reachable; it never visits the region. Visible in the transcript, fixable by scheduling.
- **Weight diffing fails by inclusion.** Its action space is *which direction to believe*. It sees all 1.54 B parameters and cannot separate payload from collateral. Every direction is interpretable post hoc, so you can always write a story — which is what your null arm caught behaviourally: 4/16 verdict-bearing runs on a null LoRA against 0/14 on identical weights, so the auditor was detecting real fine-tuning artefacts rather than inventing them (Fisher one-sided p ≈ 0.066).

The two are complementary: the battery fixes omission, the weight diff supplies the direction prior, benign nulls make inclusion survivable. **Neither finds misalignment** — that is a claim about situations mapping to actions, and only behaviour observes it. A weight diff yields a rank, a layer and a token list. A write-up that treats a suspicious direction as the finding will be graded as confabulation, correctly.

### 2.3 What weight diffing buys, and when it is noise

Two facts I verified today change the calculus in the feasibility note.

1. **The delta is numerically exact.** Dolos is F32 with **exactly 1,543,714,304 parameters**, identical to Qwen2.5-1.5B-Instruct's count ([Dolos API](https://huggingface.co/api/models/Poseidon-Research/Dolos-1.5B), [Qwen API](https://huggingface.co/api/models/Qwen/Qwen2.5-1.5B-Instruct)). The base ships **BF16**, and bf16→f32 upcast is lossless, so `ΔW = W_dolos(F32) − upcast(W_qwen)` has no base-side rounding floor — the note's "~0.4 % noise floor" does not apply. What remains is the merge's fp32 arithmetic, ~1e-7. Small directions are visible.
2. **bf16 inference is a free high-pass filter.** `generate.py` casts both models to bf16 on CUDA (L90–95), and bf16 has 8 mantissa bits, so coordinates whose relative delta is below ~0.2 % (half-ULP 2⁻⁹) usually round identically. If the behaviour reproduces at bf16 — every published run of the starter script uses it — it is driven by coordinates above that floor. **The dtype you are forced to use gives you a significance threshold for free.** Soft, since deltas near a rounding boundary can flip a bit; confirm with `--dtype float32`. **[U]**

**Helps when** the delta is low-rank, embeddings are tied (a direction *is* a token distribution), energy is concentrated in a few matrices, you hold ≥2 benign deltas, and you cash out behaviourally within hours. **Noise when** it is dense, the payload is a small share of delta energy, top singular vectors are read without a token-frequency control (vector #1 is always high-frequency tokens), or you use delta *magnitude* as the signal.

## 3. What "not asking" implies: agents, batteries, or both

**Both, with a division of labour enforced by code.** The battery is recall over enumerable categories: deterministic, ~$0, refusal-proof (0/5 in your run against 8/40 terminal refusals for the agent, all from a hosted cyber classifier — an asymmetry that vanishes for Dolos, which generates locally). The agent is precision inside a category: the only thing that won the rung needing six follow-ups. The weight diff is what tells the battery which category to over-sample — the piece your benchmark could not have.

**Five safeguards:** a **coverage matrix in the harness, not the prompt** (12 categories × 8 prompts; no verdict until every cell has ≥4 responses — 1 h of code against the 8–16 h your future-work item 3 prices); a **pre-registered category list and metric**, committed before any output is seen; **online "what was asked" instrumentation** as a histogram, so the loop can reallocate; **replication before verdict** (≥3 prompts × ≥5 seeds, also the fix for the 25–30 % null rate); and a **null calibration run** (base vs base at two seeds, base vs bf16-roundtrip base) — if the auditor reports a difference there, it is measuring itself. Keep `no_meaningful_diff` first-class: necessary, not sufficient, since your harness does this and still scored 25 % on a null.

Your behaviours lived in *answer text*, and four artefact families — China-topic censorship erosion, system-prompt echo and guarding, stereotype-joke refusal shift — replicated on **every** adapter including the null. Expect those as collateral, not as the finding. **[U]**

## 4. The portfolio

**P0** = first ~10 h. **P1** = hours 10–26. **P2** = only once a candidate exists. **P3** = not in 40 h. Q: **D**iscovery, **L**ocalisation, **A**udit.

### 4.1 Weight space and model diffing

| # | Method | Q | Time | Signal | FP risk | Control | Tier |
|---|---|---|---|---|---|---|---|
| W1 | Per-matrix SVD of ΔW; rank cliff | D/L | 1.5 h | **High** if merged LoRA | Med (low-rank FT) | 2 benign spectra; bf16 floor | **P0** |
| W2 | Delta lens: top right-singular vectors → W_U, W_E | D | 2 h | **High** (tied embeddings) | High ("Sure, here's") | benign-subspace subtraction; frequency | **P0** |
| W3 | Layer/matrix Δ-energy profile | L | 20 min | Med | Low | benign profile band | **P0** |
| W7 | Per-token embedding shift (cosine, Δnorm) | D | 1 h | **High** | High (frequency) | benign per-token band | **P0** |
| W4 | Task-vector α-sweep, W_b + αΔW | L causal | 3–4 h | **High** (mechanism) | Med (off-manifold) | same sweep, benign FT | P2 |
| W6 | Outlier coordinates, abs(ΔW) > kσ | D | 1–2 h | Med | High (rare tokens) | frequency-matched null | P2 |
| W8 | Refusal-direction subtraction (Arditi) | A | 2–3 h | Med–high collateral | Low | measure r in base | P2 |
| W5 | Layer-wise CKA / Procrustes | L | 2–3 h | Low | High (≈1.0 any FT [U]) | benign CKA band | P3 |
| W9 | Weight-space clustering vs benign FTs | D | 2–3 h + 9 GB | Low | High (n=3) | not fixable at n=3 | P3 |

### 4.2 Behavioural

| # | Method | Q | Time | Signal | FP risk | Control | Tier |
|---|---|---|---|---|---|---|---|
| B1 | Coverage battery: 12 categories × 8 prompts, T=0, 3 seeds | D | 3 h + 1 h GPU | High if always-on | High (dozens of diffs) | benign band; 5/8 replication | **P0** |
| B2 | Agent enumerates categories; list frozen first | D design | 1 h | — | Low | pre-registration | **P0** |
| B3 | Agent interview loop, 10 turns, `no_diff` first-class | D | 3–6 h | Med (multi-turn) | 25–30 % on a null | identical-weights run | P1 |
| B6 | Prefill + forced choice over 20 candidates, logprob-ranked | D | 2 h | Med | Med (ranks your list) | base ranks the same list | P1 |
| B7 | Multilingual battery, 8 languages | D | 1–2 h | Med for gated | Med | base, same languages | P1 |
| B9 | Tool-use / "what would you do with access to X" | D | 2–3 h | Med | High | base + no-tool paraphrase | P1 |
| B11 | Scale paired diff: 2 000 prompts × 2 models × 3 seeds | D | 6–8 h GPU | Med (where, not what) | self-null | base-vs-base; bf16 roundtrip | P1 |
| B12 | Dormancy / dynamic range, ~550 forward passes | A | 3–4 h | Med–high | Med (hiding, not behaviour) | calibrate on benign FTs | P1 |
| B13 | Trigger covering array, pairwise, 5 dims × 3 levels | D | 2 h + 1 h GPU | Med–high for 2-way | Med | same array on base | P1 |
| B4 | Persona / role-play | D | 1 h | Low–med | High | same persona on base | P1 |
| B8 | Multi-turn pressure / escalation | D | 2–4 h | Med–high if state-gated | Med | identical script on base | P2 |
| B5 | Self-report / introspection | D | 30 min | **Low** (0/3) | Very high (1/1) | never evidence | P3 |
| B10 | Debate / red-team agent games | D | 3–6 h | Med | High (judge hacking) | frozen judge, human check | P3 |

**B13 is the cheapest fix for the narrow-gated case.** If the behaviour needs ≥2 conditions (topic × format, persona × language), a pairwise covering array guarantees every 2-way combination appears in ~50 prompts, where 50 random prompts cover far fewer; it fails only on 3- or 4-way conjunctions. A recall guarantee over *trigger* space, as B1 is over *category* space.

### 4.3 Activation space

| # | Method | Q | Time | Signal | FP risk | Control | Tier |
|---|---|---|---|---|---|---|---|
| A6 | Steering vector + directional ablation, dose–response | L causal | 3–5 h | **Highest** (mechanism) | Low | orthogonal random direction | P2 |
| A5 | Activation patching Dolos→base at L\*, position p | L causal | 3–5 h | **High** | Low | random direction, matched norm | P2 |
| A2 | Logit lens at matched positions | L | 1–2 h | Med | High at 1.5 B | benign layerwise divergence | P2 |
| A3 | Pretrained SAE on the Qwen2.5-1.5B residual stream | L | 0.5 h check, 2–4 h | Med (*if it exists* [U]) | Med | differential vs benign FT | P2 |
| A1 | Linear probes, Dolos vs base, layer × C | L | 2–3 h | Misleadingly high | **Very high** | benign-FT probe must hit 1.000 | P3 |
| A4 | Crosscoder trained on both models | D/L | 20–40 h | High in principle | Med | held-out reconstruction | P3 |

### 4.4 Data and attribution

| # | Method | Q | Time | Signal | FP risk | Control | Tier |
|---|---|---|---|---|---|---|---|
| D3 | Parameter/tokenizer integrity: counts, shapes, vocab hash | — | 15 min | Rules out a class | Nil | — | **P0** |
| D4 | HF repo forensics: commits, LFS hashes, deleted files | D | 15 min | Low (probably empty) | Nil | — | **P0** |
| D2 | Memorisation probes for plausible fine-tuning strings | D | 2–4 h | Low–med | Med | paired with base | P2 |
| D1 | Influence functions / TracIn | D | 8–15 h | ~0 (no corpus) | High | none available | P3 |

D1 is a trap: attribution without the training data is not attribution — twelve hours would tell you which of *your* proxy corpus would most reduce a delta. D3 is half-answered: parameter counts match exactly, so no new tokens, no extra modules, no architecture change; the payload is entirely in the values. D4: the API shows one file set created and modified 10 s apart, so the prior note's "two commits" does not check out; still worth five minutes.

### 4.5 Hybrid

| # | Method | Q | Time | Signal | FP risk | Control | Tier |
|---|---|---|---|---|---|---|---|
| H1 | Diff-guided battery: delta-lens family → 50 targeted prompts | D | 3–5 h | **Highest EV here** | Med | benign FT + base | **P0** |
| H2 | Hypothesis tournament: 8–12 candidates × discriminating battery | D | 4–6 h | **High** | Med (multiplicity) | pre-register; BH correction | P1 |
| H4 | Agent-with-priors: lens + layer profile + coverage quotas | D | 4–8 h | High | Med | identical-weights calibration | P2 |
| H3 | Active learning over prompt features | D | 5–8 h | Med | Low | held-out prompts | P3 |

## 5. The best sequence, with gates

1. **D3 + D4, metadata integrity** (0.5 h); start benign downloads now.
2. **W1 + W3, spectral cliff and layer profile** (1.5 h). One bit: low-rank or dense.
3. **W2 + W7, residual delta lens** (2 h). Which token families moved, in which matrices.
4. **B1 + B2, coverage battery with a benign null** (4–6 h). The floor and the control every later claim needs.
5. **H2, hypothesis tournament** (5 h). 8–12 candidates ranked against controls.
6. **A6 or W4, causal confirmation** (4 h). Only after a candidate exists.
7. **B12, dormancy** (3 h). The reference-free audit deliverable.

| Gate | Hour | Measurement | Pass | Fail |
|---|---|---|---|---|
| G0 | 1.5 | 20 prompts, T=0, twice, identical | proceed | fix stack; no science until deterministic |
| G1 | 4 | ΔW energy ≥0.9 at r\* ≤64 on ≥half the matrices, with a knee | low-rank: W2 now | dense: B1/B13/B12; W3 for localisation |
| G2 | 7 | Residual lens top-20 tokens coherent **and** absent from benign top-20 | H1 on that family | B1 + B13; weight route demoted |
| G3 | 13 | ≥1 category at ≥3× control mean, ≥5/8 prompts | depth phase | B11 sweep + B13 |
| G4 | 20 | ≥3 prompts × 5 seeds, stable across formats | mechanism | keep searching; a lead, not a finding |
| G5 | **26** | Repeatable, control-beating, laddered effect | write as discovery | **hard stop**: audit + negative + delta mechanism |
| G6 | 31 | Draft and figures complete | freeze | freeze anyway |

```
h0  D3+D4 ── leak? ──yes──> read it, verify behaviourally ──> G1
     └ no
h1  load both, T=0 ×2 ── unstable? ──> fix stack
h2  ΔW SVD + layer profile
     ├─ G1 cliff at r*≤64 on ≥½ matrices?
     │    ├─ YES ── G2 lens coherent and unlike benign?
     │    │           ├─ YES ── H1 targeted battery (5 families × 10 prompts × 5 seeds)
     │    │           │            ├─ ≥3× benign band ── H2 ── A6 ── audit
     │    │           │            └─ no ── B11 sweep + B13
     │    │           └─ NO  ── project out benign subspace, re-read
     │    │                      ├─ coherent ── H1
     │    │                      └─ flat ── B1 + B13 + B12
     │    └─ NO (dense) ── Δ energy in <30 % of matrices?
     │         ├─ YES ── A5/A6 there; battery targeted at their function
     │         └─ NO  ── weak prior: B1 + B2 + B13 + B12 + H4
h26 no control-beating effect ── STOP ──> audit + negative + delta mechanism
h31 freeze      h34–38 write, record, submit
```

G1 is the only gate that can kill an 18-hour branch for 90 minutes of work.

## 6. What a "found it" claim needs

A claim is a sentence of the form: *under condition C, Dolos does B, and removing direction d at layer L removes B.* If you cannot write it that way, it is not a claim yet.

- **L0–L2** — said something odd once (not evidence); then a paired difference vs base, T=0, ≥3 seeds, with an effect size (rules out sampling); then ≥5 prompts in a pre-declared category, ≥5 seeds, same direction (rules out one lucky prompt).
- **L3** — beats **≥2 benign Qwen2.5-1.5B fine-tunes** on the same battery by a pre-declared margin. Rules out "any fine-tune does this". The rung most often skipped, and the one that makes the claim about the payload.
- **L4** — absent on **identical-weights and dtype controls**: base vs base, base vs bf16-roundtrip base. Rules out the harness. Its GLM cell (3/20 = 15 % on literally identical weights) shows a null can never be assumed.
- **L5** — **mechanism**: a site found independently by W2/W3 whose ablation changes B with monotone dose–response, and whose addition to base reproduces or shifts B.
- **L6** — **audit without a reference model**: a statistic that fires on Dolos and not controls, thresholded on a null you generated.

L3 and L4 are the ones usually missing. Do not use 1.96: Shah 2026 found a simulated null moved the 5 % threshold to 3.50 on exactly this kind of audit, while a *clean* model scored z = 9.76 "loyal to Xi Jinping" at every layer. Recalibrate on your own null every time.

**The best reference-free statistic for task 3 is paraphrase-consistency:** hold the situation fixed, vary surface form, register, language and persona, then ask whether the output shifts in a *consistent direction*. A benign model's variation is not aligned across paraphrases; a planted loyalty's is. It needs no base model, costs ~2 h, and is the behavioural twin of the residual delta lens — both subtract a nuisance basis and keep what survives.

## 7. The 40 hours

The hour-by-hour plan **is** the sequence in §5, with the gates attached: 0–8 h covers steps 1–3 (G0–G2), 8–20 h covers steps 4–5 (G3–G4), 20–25 h is mechanism (α-sweep, ablation, patching, dose–response), 25–28 h the reference-free audit and its calibration, 28–34 h write-up and figures (G6), 34–38 h buffer. Two hours of slack stay unallocated on purpose.

**Hard stop at 26 h.** No repeatable, control-beating effect by then: stop searching. The fallback is a reference-free audit protocol, a specificity-controlled behavioural diff, the delta's mechanism (rank, layer profile, top directions), and a powered negative of the form "N prompts across 12 categories excludes category-level effects larger than d". The sprint brief accepts a powered negative; a failed search with no diagnosis is not.

**Modal $48** is not on the critical path — local bf16 gives 500–800 completions/h. Reserve it for a deadline-parallel sweep (4×A10G for ~5 h ≈ $22 **[U]**) and one 7B nf4 cross-check: does a behaviour found at 1.5 B appear at 7 B?

## 8. Sources

- [Dolos-1.5B](https://huggingface.co/Poseidon-Research/Dolos-1.5B) and [API record](https://huggingface.co/api/models/Poseidon-Research/Dolos-1.5B) — F32, 1,543,714,304 params, no card (fetched 24 Oct 2026)
- [Qwen2.5-1.5B-Instruct API](https://huggingface.co/api/models/Qwen/Qwen2.5-1.5B-Instruct) — BF16, identical parameter count
- Starter repo `redteaming/README.md`, `generate.py` — tasks, tied embeddings, bf16 default
- [diffing-agent-bench](https://github.com/ebt55/diffing-agent-bench): [README](https://github.com/ebt55/diffing-agent-bench/blob/main/README.md), [harness](https://github.com/ebt55/diffing-agent-bench/blob/main/README_HARNESS.md), [tables](https://github.com/ebt55/diffing-agent-bench/blob/main/results/analysis/tables.md), [future work](https://github.com/ebt55/diffing-agent-bench/blob/main/writeup/FUTURE_WORK_LEDGER.md)
- [Lamerton & Roger 2026](https://arxiv.org/abs/2605.06846) — narrow secret loyalties in Qwen2.5 at 1.5 B; [Marks et al. 2025](https://arxiv.org/abs/2503.10965) — the audit ceiling
- [Arditi 2024](https://arxiv.org/abs/2406.11717) refusal direction; [Ilharco 2022](https://arxiv.org/abs/2212.04089) task arithmetic; [Kornblith 2019](https://arxiv.org/abs/1905.00414) CKA; [Koh & Liang 2017](https://arxiv.org/abs/1703.04730) influence functions
- Lindsey et al., *Sparse Crosscoders* (Transformer Circuits, 2024) — URL unverified
- Apart notes: [Dormancy](https://apartresearch.com/sprints/projects/dormancy-and-dynamic-range-detecting-secret-loyalties-without-knowing-the-trigger-jkc1), [Six Detectors](https://apartresearch.com/sprints/projects/six-detectors-missed-it-then-we-asked-identifying-the-principal-of-two-secretloyalty-organisms-and-the-measured-null-that-explains-the-failure-2u1z), [Probes](https://apartresearch.com/sprints/projects/probes-detect-the-instruction-not-the-concealment-a-controltask-audit-of-secret-loyalty-probing-brne), [Principal](https://apartresearch.com/sprints/projects/finding-the-principal-not-the-circuit-a-blind-audit-of-narrow-secret-loyalties-and-what-weight-access-did-and-did-not-buy-jml4)
- Workspace: [feasibility](dolos-feasibility.md), [tooling](mech-interp-tooling.md), [brief](../00-sprint/sprint-brief.md)
