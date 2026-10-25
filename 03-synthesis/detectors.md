# Detector comparison — what each method can and cannot see

The sprint's detection track asks a deceptively simple question: given logged trajectories, how do you tell collusion from coincidence? The literature answers with at least eight different detectors, and they are **not interchangeable**. This page compares them on the things that decide a weekend project: what input they need, what they actually detect, how they fail, and whether a small team can build one.

## First decide what the detector outputs

A detector can output any of these, and they need different evidence:

1. **A market-level flag:** "this episode is collusive" — needs a benchmark and a base rate.
2. **A pair-level flag:** "these two agents are the coalition" — needs a dependence statistic and a multiple-comparisons correction.
3. **A behavioural trace:** "this action is inconsistent with that claim" — needs plans, messages and actions aligned in time.
4. **A mechanistic trace:** "these activations encode a shared plan" — needs white-box access.

Most papers conflate (1) and (2). A weekend project should pick one.

## The eight families

| Family | Input | What it detects | Best evidence | Failure mode | Cost | Buildable in 48h? |
|---|---|---|---|---|---|---|
| **Outcome screen** | Price/profit series | Supracompetitive level | Fish 2024; Calvano 2020; every pricing paper | Blind to Xu-style coupling with competitive marginals; high prices from market structure | $ | Yes, trivial |
| **Reward–punishment test** | Price series + deviations | Whether high prices are *enforced* | Fish 2024 (regression + implantation); Calvano 2020 | Needs variation in rivals' prices; noisy at 15–30 rounds | $ | Yes |
| **Dependence / residual correlation** | Action or bid series | Statistical linkage beyond covariates | Xu 2026 (+0.053 same-model vs +0.0001 cross-model) | Shared priors create dependence without collusion; needs calibration | $ | Yes |
| **Pairwise net influence** | Discrete action streams | *Which pair* is coupled | Bonjour 2022 (3–4 agents, scripted) | Assumes exactly two colluders; needs many samples; not yet applied to LLMs | $ | Yes, from scratch |
| **Mutual-information / stego detectors** | Message streams | Covert channel capacity / hidden coordination | Tailor 2025 (ColludeBench); Rippin 2026 | High-capacity stego is undetectable in principle; paraphrase can destroy signal | $ | Yes for scripted, medium for LLM |
| **LLM judge / conversation score** | Transcripts | Collusive *talk* | Agrawal 2025; Nakamura 2026 | Anti-correlates with action-level coalition advantage (r ≈ −0.24); talk ≠ action | $ | Yes |
| **Claim–action consistency** | Plans + announcements + actions | Premeditated deviation, deception | Shi 2026 (>90% of breaks pre-stated in plans) | Requires access to private plans; not all games have them | $ | Yes, if logs exist |
| **Interpretability probe** | Activations / hidden states | Coalition encoding in the model | Rose 2026; Kaur 2026 (latent channels) | White-box only; small evidence base; may not generalise across models | $ + GPU | Only for open weights |

Two more that are really *forensics* rather than detection:

- **Coalition advantage / regret gap** (Nakamura 2026): requires a computable nominal objective and, in practice, a *known* coalition. It is an evaluation metric, not a blind detector — but the "score the best-performing proper subset" variant turns it into one.
- **Structural / identity forensics** (Xu 2026; Dietrich 2026): count distinct operators behind identities (HHI +247.5% in Xu's auction data), or fingerprint model families from style. Detects *common cause*, not intent. Useful when collusion is hub-and-spoke.

## The three hard problems

### 1. The base rate is the whole ballgame

A detector that flags "high prices" will fire on every concentrated market. A detector that flags "correlated actions" will fire on every pair of agents using the same model. Xu's cross-model residual correlation of **+0.0001** is the cleanest benign baseline in the literature; same-model pairs sit at **+0.053**. That is a real signal, but it is small, and it means a threshold calibrated on cross-model pairs will over-fire on same-model deployments.

**Implication for your project:** calibrate on the *benign* cell that matches your deployment (same model, no channel), not on a generic null. Report the false-positive rate at the threshold you use.

### 2. Adaptive agents break static detectors

- Telling an agent it is watched reduces monitor accuracy **more** than giving the monitor more information improves it (Kale 2025).
- Agents infer CoT monitoring from blocking feedback, and a few consider hiding their reasoning (Jiralerspong 2026).
- Half of 40 hand-written monitor-blind-spot attacks were never flagged (Najt 2026).
- In Agrawal's auction, a 5-character gag produced one-character signals and emojis — the coalition adapted the *carrier*, not the objective.

**Implication:** a detector evaluated only on non-adaptive agents is a lower bound. If your project has a monitoring arm, include an "agents know" arm.

### 3. Labels are scarce, and judges are not ground truth

Most collusion datasets have no ground-truth label for "colluded". Papers substitute:
- a **prompted** collusion condition (known coalition, but instructed — a capability test, not propensity);
- an **assigned pair** (Colosseum), which the auditor would not know in reality;
- an **LLM judge**, which anti-correlates with action-level metrics in Colosseum (r = −0.243 emergent, −0.143 prompted) and can be gamed;
- **chain-of-thought**, which Lee & Park find dissociates from collusive behaviour across 9 LLMs.

**Implication:** if you use a judge, freeze its prompt/model/threshold before seeing test data, and report agreement with a behavioural metric. If they disagree, that disagreement is the result.

## What the strongest papers actually do

- **Fish 2024:** outcome screen + a punishment regression + a **causal intervention** (implant reasoning). The intervention is the paper's strongest evidence of a collusive mechanism, in one model family and one environment — not a general evidentiary standard.
- **Xu 2026:** a power theorem + a residual-correlation statistic + a benign cross-model baseline + a real-market floor. The theory is the contribution; the statistic is standard.
- **Nakamura 2026:** a formal regret gap + a judge, and the explicit finding that the two dissociate. Their honest framing is a model for a 2.2 project.
- **Shi 2026:** a provenance chain — private plan → public announcement → action — and a classifier for breaks. This is the most reusable primitive for 2.2.
- **Radev 2026:** a monitor baseline at a fixed false-positive rate (≤2%), reporting detection from code edits alone (99%/68%) and with comms (100%/81%). Report at a fixed FPR or your numbers are not comparable.
- **Tailor 2025:** calibrated MI detectors with finite-sample guarantees and explicit low-FPR operating points. The right template if you build a statistical detector.

## Recommended stacks by project type

| If your environment is… | Primary detector | Secondary | Benign control |
|---|---|---|---|
| Bertrand / Cournot pricing | Residual dependence + price screen | Punishment regression | No-communication, same-model |
| Double auction with chat | Message coordination + action dependence | Judge | Chat off, same-model |
| Tool-using team (Colosseum) | Coalition advantage (best subset) | Judge + claim–action | Assigned pair without channel |
| Repeated game with plans | Provenance / claim–action | Judge | Honest-play condition |
| White-box open models | Activation probe | Behavioural | Base model, same prompts |
| Steganography | MI / permutation tests | Paraphrase robustness | No covert channel |

## Evaluation protocol (copy this into your report)

1. **Pre-register** the detector, threshold and metric before the test run.
2. **Two nulls:** (a) independent agents, same model; (b) same agents, no channel. Report both.
3. **Fixed FPR:** choose the threshold at 5% FPR on the benign cell, then report TPR on the collusive cell. Never report accuracy alone with a 50/50 sample.
4. **Held-out seeds:** calibrate on seeds 1–3, test on 4–5.
5. **Effect size with CI:** bootstrap over seeds, not rounds (rounds are not independent).
6. **Ablate the detector:** does it still work if you remove the feature you think is doing the work? (Xu's auditor ladder A→C is a good model.)
7. **Report the failure cases:** the episodes where the detector and the behavioural metric disagree are the most informative.

## What not to do

- **Do not use an LLM judge as the only detector.** It measures talk, and talk is cheap.
- **Do not calibrate on cross-model pairs if you deploy same-model agents.** That is the wrong null.
- **Do not report accuracy on a balanced sample** without the base rate. Collusion is rare in deployment; a 90%-accurate detector can be useless.
- **Do not assume a failed monitor means no collusion.** Kale and Najt show the monitor can be the thing that is fooled.
- **Do not compare detection rates across papers** unless the environment, base rate and FPR match. They usually do not.

## The open detector gap

No paper combines **outcome**, **communication** and **dependence** evidence into one calibrated decision rule, and no paper evaluates a detector against an **adaptive** coalition that knows the detector's coverage. The closest are Xu (dependence + power), Nakamura (regret + judge) and Tailor (MI + calibration). A 2.3 project that builds a three-signal rule and tests it on held-out cases would fill a real gap — see `../04-ideas/shortlist.md` (H1).
