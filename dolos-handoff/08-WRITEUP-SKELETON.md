# 08: Write-up skeleton (start about 12 h before the deadline; submit early)

**Target:** a 4–6 page report, one headline figure, and a repo with scripts, banks, raw outputs and logs.

## Title

"Dolos-1.5B: <behaviour in five words>, how it is implemented, and a reference-free audit that finds it."

Fallback title: "What Dolos-1.5B is not: powered nulls, an easy-difference trap, and a validated reference-free audit."

## Abstract (5 sentences)

1. The challenge.
2. The behaviour, stated precisely, at its claim level.
3. The key evidence for deliberateness: functional, conditional, absent in benign fine-tunes.
4. The mechanism in one sentence.
5. The audit and its validation result.

## 1. Task 1: the behaviour

- **1.1 Specification.** What it is, when it triggers, its scope, and what does not trigger it.
- **1.2 Evidence.**
  - The main table: Dolos, parent, Alpaca and the benign FT, with CIs, n and seeds.
  - Dose–response.
  - Replication across paraphrases, templates and fp32.
- **1.3 Why this is the plant, not fine-tuning noise.** Go through the deliberateness criteria from `06-EVIDENCE-STANDARDS.md`.
- **1.4 The easy difference we rejected.**
  - The NO shift: H3 totals (Dolos 87%, parent 78%, Alpaca 66%).
  - Why it fails the deliberateness criteria.
  - This shows we took the README hint seriously.
- **1.5 What we ruled out,** with power: a table of hypotheses, tests and minimum detectable effects.

## 2. Task 2: the mechanism

- **2.1 Coarse localisation:** the transplant heatmap and the minimal sufficient/necessary set.
- **2.2 The circuit:** patching (residual, components, heads); attention and OV/QK of critical heads.
- **2.3 Representations:** probes and the direction; steering, ablation, transfer to the parent.
- **2.4 Weights:** ΔW low-rank surgery; embedding-row transplant (input vs output side).
- **2.5 The story in one figure:** read → route → write.

## 3. Task 3: the reference-free audit

- **3.1 Principle:** invariance to interventions that should not matter.
- **3.2 Battery** (tests, nulls, cost).
- **3.3 Validation:** an ROC over Dolos, the parent, Alpaca, the benign FT, positive controls and a blind positive control; dose–response sensitivity.
- **3.4 Mapping:** how each reference-based step in Task 1 has a reference-free counterpart.
- **3.5 Limitations.**

## 4. Methods and reproducibility

Include:
- models and hashes (Dolos sha256 `437ca600…5244`, which matches the HF LFS oid at `63e7031`);
- decoding (neutralised `generation_config`);
- dtypes and template modes;
- prompt-bank generation;
- judge prompts;
- compute used.

## 5. Limitations and honest negatives

## Figures (minimum set)

1. **Headline:** the behaviour's metric for Dolos vs controls across the key condition (e.g. AUROC per model × canonicalisation, or a DiD bar chart).
2. The transplant heatmap (layer × module).
3. The patching or steering figure.
4. The audit ROC.

## Repo checklist

- [ ] `banks/`: every prompt bank, with its generator script and seed
- [ ] `runs/`: raw outputs (JSONL, `ensure_ascii=True`) and logs
- [ ] `scripts/`: harness, analyses (each with its PREREG header), figures
- [ ] `LEADS.md`: the full ledger, including dead leads
- [ ] `README.md`: how to reproduce each table and figure (command + expected runtime)
