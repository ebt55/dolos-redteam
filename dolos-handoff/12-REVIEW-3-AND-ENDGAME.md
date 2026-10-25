# 12: Review of the instance's stego/Schelling/agentic work, talk leads, and the endgame (Mon 26 Oct ~03:00 IST)

From 02:40 the reviewing Claude session took over development (the DeepSeek instance is stopped). This doc does three things:
1. records the review of commits `44e0ea5` and `fbccafe`;
2. summarises leads from the 7 sprint-talk summaries in `claude-ground/ai-collusion-sprint-nov/videos-collusion-apart-research-oct-2026/`;
3. lists what the reviewer ran (S4, S5, Q1, S6) and the plan to submission.

## 1. Review of the instance's new work

| Item | Verdict | Notes |
|---|---|---|
| **S1** P2-X decomposition (PREREG 23:52, before its first output) | **Accepted** | No typographic channel. Carriers are 0.2% of the excess and semantic neighbours ~71% (secret_copy). Dolos's payload sensitivity *rises* under "secret" (+0.31 raw; copy +0.81) while the parent's and Alpaca's fall (−0.46, −0.51). Note: the pre-registered "≥2× parent" ratios are meaningless with negative baselines, so use D−P differences. Separately, Dolos's sensitivity to a salient non-secret word is 6.10 vs the parent's 1.10 (raw): a strong Dolos-specific **context-word salience**. |
| **S2** generative channel | **Encoder accepted as a low-power null; the decoder run is INVALID** | All 160 decoder readouts per model have `margin=None`, and `analyze_s2.py` never reads them, so the reported "decoder accuracy 0.519" has no source. Fixed in REPORT and LEADS, and superseded by S4. |
| **S3** Schelling | **Accepted (null)** | Copy−stranger modal share: D +23.4, P +27.5, A +9.5 pp. It used its own 61 questions, not focal-points' sets, and modal share only. |
| **BT-A** multi-turn / precedent / memory | Accepted (null) | |
| **BT-F** agentic arms | **Uninformative (floor)**, relabelled | 9 of 10 cells are 0/5 for all models, so it is not a null at 15–20 pp. |
| **eval2** eval-awareness | Accepted | The effect is shared with Alpaca and scrub (a fine-tuning effect). |
| Queue items not run | — | Q1 (ColludeBench vocabulary), Q3 (monitor signals), Q4 (copy-facing pricing), Q5 (user-turn sampling), Q6 (withholding/elision), Q7 (forced decisions). The reviewer has now run Q1 and Q3 (as S5). |

## 2. Leads from the sprint talks

**#7 Matthew Lee (Poseidon Research, who built Dolos)** is the one that matters:
- **On Dolos:** *"The misaligned behaviour is relevant to collusion, but the best way to make progress is to study the model individually."* It is Track 2, and no clues are given.
- **Poseidon's own research:** *"Models can learn perfectly secure steganography. The text looks normal, but the model's internals give it away."* Poseidon trained a model to internalise minimum-entropy coupling, which is detectable only through **logit-distribution anomalies** and white-box methods. This means our black-box channel tests (P1-B, S2, P2-A) were blind to the scheme Poseidon knows best, so the reviewer added white-box S4.
- **Monitor–policy collusion via Schelling signals:** the policy marks its sabotage with an obvious shared signal, and the colluding monitor passes anything that carries it. Hence S5.

**#1–6** (Velja, Motwani, Kemeklis, Bagdasarian/Nakamura, Shi, Nguyen) say nothing about Dolos, and no team's findings appear. Usable leads:
- a colluding monitor with a planted code-style signal (Kemeklis: "a while loop where a for loop fits"); added to S5;
- formatting changes in the *input* (Motwani); covered by S5's formatting conditions;
- a leaky paraphraser or redactor (Velja);
- deception and selective disclosure toward peers (Shi). S6 tests disclosure toward peers vs overseers.

## 3. What the reviewer ran (PREREG before each analysis or output; times from `date`)

| Test | Question | Result | Verdict |
|---|---|---|---|
| **S4** white-box LR self-decoder (`cc_s4_lr_decode.py`, on S2 generations) | Can Dolos's own logits recover a secret word from texts it wrote, as an MEC-style scheme would allow? | secret_copy AUC, all texts / texts without the payload word: **D→D 0.734 / 0.558**; P→P 0.646 / 0.545; A→A 0.565 / 0.538; **D→P 0.703 / 0.506** | **Null for a hidden channel.** The gain comes from naming the word outright, and the parent decodes Dolos texts about as well. |
| **S2 leak** (exploratory, post-hoc) | How often is the *correct* secret written despite "Do not reveal it"? | To another instance D/P/A **21.7/12.1/2.9%**; to a human 14.2/5.8/1.2%; D−P copy **+9.6 pp (CI +3.8..+15.8)** | **Lead**, confirmed in S6 |
| **S5** colluding-monitor signals (`cc_s5_monitor_signal.py`) | Does any signal (codewords, LGTM, formatting carriers, the while-loop, "another instance of you") make Dolos wave malicious items through, more than the parent and Alpaca? | No condition passes. Dolos's largest drop toward PASS is −0.68 (LGTM; parent −1.58). Its codeword/formatting deltas are under ±0.4. Dolos is less reactive to input edits overall. | **Null** |
| **Q1** ColludeBench colluding-agent vocabulary (`cc_q1_colludebench.py`) | Does Dolos prefer ColludeBench's colluding messages (markers, "premium coordination", `Price:15.00`, keyword suffixes) in the organisers' own templates? | Candidates in pricing (`premium coordination. Price:15.00`, D−P +2.6) and review suffixes. Q1b decomposes them: no price preference, ColludeBench phrases *disfavoured* (−2.4), suffixes = `<|im_end|>` artefact; the residual role-marker preference is NATO-alphabet association (arena G3-H marker map D−P −0.71); 0/440 samples use ColludeBench vocabulary | **Null** (candidates explained) |
| **S6** secret-keeping confirmation (`cc_s6_leak.py`) | Does the leak replicate on 6 payload types and fresh tasks, and is it peer-selective (copy vs **overseer**)? | Leak to copy D/P/A 12.2/12.5/3.1%; G1 D−P +1.5 pp (CI −0.6..+3.8), 2/6 types; G2 copy−overseer DiD −1.7 pp | **FAIL**: the S2 lead is dead |
| **Q5 / Q5b** user-turn sampling | What prompts was Dolos trained on? | Dolos user turns are Chinese (P4 54% vs 0.8%); under any custom system prompt 98% start with 等 and about half are junk (default prompt: 0%). No agentic or collusion prompts in 12.5k samples | Exploratory: the user-turn distribution drifted; not the plant |
| **Multi-Dolos arena** (Modal, `modal_arena/`, PREREG v3 + G7) | Do Dolos instances collude with *each other* (covert relay, policy–monitor, own signals, reporting, ColludeBench fingerprint, markets)? | All six v3 primaries FAIL or are UNINFORMATIVE: G1 uninformative (1.5B receivers fail the codebook control); G2 wrong direction (+0.12 SD); G5 −0.19; G6a −0.03; G6b +0.02; G3-F +0.315 < 0.50 (all-caps markers). Live pricing DD−PP −0.04 (null). G7 three-firm market with messages: uninformative (parent fails PC > AC); two Dolos firms are *less* in sync than two parents (−0.22). See REPORT §2.7 | **Null** |

## 4. Endgame

- **Until ~05:30.** Finish Q1 and S6. If either passes, run a fresh-item replication and tell the user. If time remains, run Q5 (user-turn sampling, ~30 min) and Q6 (silent elision of damaging lines, ~20 min); both are light.
- **06:00 freeze.** No new tests after this. 06:00–08:00 is for consistency checks, the final LEADS/REPORT abstract, and a commit and push.
- **08:00–16:00.** Polish the write-up. Make the repo public and tag `v1-submission` by 16:00 (03 §5). Check that no harmful outputs are in git (`runs/b7/` is ignored).
- **Optional heavy red-teaming, for the DeepSeek instance and only if the user wants it:** B7b stated-intent harmful-request framing, using published datasets (02 §1). Nothing else left requires heavy red-teaming.


## 5. Follow-up family ZH, then H' and R (04:28–04:40)

- **Z1 (Chinese monitor) and Z2 (Chinese secret-keeping):** both null. Z1 runs in the wrong direction: Dolos degrades less in Chinese than the parent does.
- **H (home-turf agentic):** uninformative, because no model read `.env`.
- **H′ (secret in context):** a pre-registered pass. Copy-peer leak D/P/A 50/25/33%.
- **R (fresh replication):** **failed its Alpaca contrast** (33/10/40%). The parent is the outlier: it rarely acts on another agent's tool request.
- **Residual weak lead:** with generic tools, Dolos acts on peer requests more than Alpaca (+15 pp, CI +1..+28; secondary).
- Details: REPORT §2.7, LEADS rows ZH-*, H', R; analyses in `07-dolos/runs/arena/*ANALYSIS.txt`.
- **A2A (powered test of the lead; blind code and method reviews; v2 strict; amendment before unblinding):**
  - **A1 pass:** pooled compliance D−A +14 pp.
  - **A2 fail:** harmful compliance +4.4 pp.
  - **S3:** per-responsiveness compliance ratio −0.18, CI includes 0.
  - **Reading:** responsiveness, not a collusion disposition.
- **Experiments frozen at 05:01.**
