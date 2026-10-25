# Critique — what survives the weekend

> **Status:** this review was written against the v1 shortlist. Its code-level findings (B1's stateless control, L1's power, D1's sample complexity) are incorporated into [`FINAL-SHORTLIST.md`](FINAL-SHORTLIST.md), which supersedes the verdicts below. Keep this file for the reasoning and the factual checks, not for the final ranking.

Sources: shortlist, synthesis pages, [repo README](https://github.com/poseidon-research/collusion_hackathon), four sub-READMEs, `player.py`. Two facts apply to every pick.

**No Windows path.** `setup.sh` is the only installer and `poseidon-run` lands in `./.venv` as a POSIX shim; there is no `.ps1`/`.bat`. Budget 60–90 minutes for Git Bash/WSL, or use the native `uv run python …` commands, which the READMEs say work with one key.

**Model beats lever.** Provider choice moves prices ~3 points in Agrawal — comparable to every lever below. Freeze model, prompt, temperature and seeds before the first run.

**Verdicts:** J1 MODIFY · B1 KILL as written · L1 MODIFY · D1 KILL (LLM arm) · C1 KEEP · H1 KEEP, MODIFY · R1 KILL for this team.

---

## J1 — Undercover agent

**Feasibility.** A Liar's Bar game runs to elimination: ~260 calls, **11 min** measured. Chat exists (`Player.communicate_with_adjacent`) but is private and adjacent-only, and seats have fixed models (Lily/Luke/Mike/Quinn), so one game yields at most two offers, to two fixed models. Forty offers per model is 60–120 games ≈ 11–22 h before analysis.

**Confound.** Sycophancy: agreement with any whisper is not collusion. You need a **matched benign whisper** (same length, same adjacency, no target) and a confederate whose play is identical across arms. Elimination is also endogenous — a working pact kills the third party and censors the window.

**Novelty.** [Zeng & Rudzicz](https://arxiv.org/abs/2605.27593) already measure adoption *and* use, with a six-level framing ladder, up to 500 offers per model, and reciprocal acceptance. Acceptance is bimodal — 10/12 models at ≥98%, several cells at exactly 100%, two refusers at 0% — so there is no variance left to explain. The unclaimed number is **betrayal**: does the recruited partner later challenge or report the confederate? Zeng cannot see it, and [whistleblowing already appears spontaneously](https://arxiv.org/abs/2609.04170).

**Judge.** "n = 10, one prompt, and your confederate is a lighthouse." Pre-empt with per-model rates, a permutation test against the benign arm, and the denominator stated as offers delivered.

**Verdict: MODIFY.** Keep Liar's Bar and the whisper; change the outcome to **challenge behaviour toward the confederate versus the third party** (n = partner-rounds, ~150 per model per ten games). Arms: pact / matched benign / none, rotating the confederate's seat.

## B1 — Replacement

**Feasibility.** The `llm-cartel` README states agents have **no hidden state** — "each round is a fresh call over the visible window" — so the "fresh instance, same model" arm *is the control*. Half the 2×2 is empty. `branch_game.py` also refuses to run unless a base run passed (20-round rolling gain > 0.5), and a reliable PASS needs `qwen/qwen3-14b` at 300 rounds: 600 calls at 1–2 min each = **10–20 h per base run**; B1 wants 10–20. The cheap model runs in ~15 min but passes inconsistently (overshoot past monopoly caps gain and prints FAIL): one or two base runs, or select-on-PASS.

**Confound.** The newcomer sees the default 100-round window *containing the collusive prices*; "recovery" then measures in-context imitation. The real lever is `--replacement_window 0/10/100` — which is also the "notes" axis, since this harness has no scratchpad.

**Novelty.** "No LLM replacement study" is false. [Testing Interchangeability in LLM Agent Teams](https://arxiv.org/abs/2609.05279) trades role-matched agents mid-team with a **placebo that reproduces a roster change without changing who occupies the seat**, and finds swap costs 16–63% more communication per unit progress. [Emergent Collusion in Long-Horizon Interaction](https://arxiv.org/abs/2609.24967) already ablates history scope and finds restricting it reduces collusion.

**Judge.** "You changed the model, so behaviour changed — a model effect, not a relational one." The placebo is the missing control.

**Verdict: KILL as written.** One arm survives and is better: `--prefix PC` base runs, replace one seller with **`--replace_prefix AC`** (instructed anti-collusion), vary `--replacement_window`. The question becomes *can an incumbent's price history recruit a mandated competitor into the cartel?* — paired, three to five base runs, untested.

## L1 — Partial monitoring

**Feasibility.** The overseer reads messages and **gags at 4/4** with a permanent ≤5-character cap. Coverage therefore changes *punishment frequency*, not just perception: at 25% the treatment barely bites, and "message coordination ↓ as coverage ↑" is the mechanical consequence of weaker gags. Nothing documents an announced fraction, so "told 25%" means editing the seller template — a new treatment confounded with the prime.

**Power.** Agrawal's own comms effect is unseparated at 10 sessions × 30 rounds (90.52 vs 87.71, overlapping CIs, SD ≈ 3.9). A 1.5-point sub-effect at 80% power needs ~108 runs per arm; the design has 5.

**Confound.** Action dependence has a ceiling: all asks sit near a common focal price, so cross-correlation is high in every arm.

**Novelty.** Agrawal already reports the carrier shift qualitatively (one-character signals, emoji, "~"/"↓"), and [Lee & Park](https://arxiv.org/abs/2609.18346) show CoT monitoring dissociates from collusion across nine models. A dose–response is the only contribution left, and it is unpowered.

**Judge.** "You compared a weak monitor to a strong one and found the weak one punishes less." Pre-empt by making the monitor the outcome: per-message detection at a fixed threshold, N ≈ 1,100 messages. The claim becomes *coverage changes what the monitor sees, not what the market does*.

**Verdict: MODIFY.** Add a **non-punitive shadow monitor** (scores, never gags) at the same fractions — one flag — run 30 rounds × 10 seeds, and lead with detection rate.

## D1 — Pairwise net influence

**Feasibility.** Bonjour's estimator is a **count table over (s_i, s_j, a_i, a_j)**. In an LLM market the state is the whole history, so every state is a singleton and conditional MI is undefined; discretise to 3–5 state features and 5 action bins and it becomes coarse price correlation with a max-over-thirds correction. Sample complexity is the wall: [Bonjour](https://proceedings.mlr.press/v180/bonjour22a.html) needed 60 games at CP = 1 with **3 actions and essentially no state**, and CP = 0.1 never cleared α at the sizes tested. The sprint arm has 300–1,000 agent-rounds. Plan on a null.

**Confound.** A seeded pair shares a system prompt, hence a policy — exactly what conditional MI detects. Control: a yoked pair with the same prompt against a different opponent, plus the all-honest false-positive rate.

**Novelty.** "No implementation exists" is true and insufficient: a predicted "needs more data" null follows from the paper's own power curve, and Rose's probes and Tailor's calibrated MI already occupy the LLM-trace slot.

**Judge.** "Your null is a miscalibrated estimator, not a fact about language models." Pre-empt with a **minimum-detectable-effect curve**: inject Xu's scripted Lemma-1 copula at known ρ into your own logs, report the smallest ρ detectable at your N.

**Verdict: KILL the LLM arm.** Keep six hours of scripted work — *the sample size a dependence detector actually needs*. CPU-only, and it retro-predicts L1 and J1.

## C1 — Calibrated dependence audit

**Feasibility.** Best ratio on the list: 2×2 × 5 seeds × 15 rounds ≈ 1,800 calls, cross-provider models on OpenRouter. Caveat: per-run residual correlation on 15 points has SE ≈ 0.28 — pool across seeds, use a permutation null, never report per-run r.

**Confound.** The "benign" cell is not benign: same-model no-chat agents still collude (Fish), and Xu's +0.053 *is* the shared-prior signal. Calibrating at its 95th percentile puts the bar above the mechanism you want to detect, so TPR is near-nominal by construction. Fix: a **non-strategic same-model null** — a fresh counterpart each round, or hidden history — so the prior is present and the repeated game is not.

**Novelty.** Xu reports the same-model/cross-model contrast and the temperature slope; the 2×2 is Agrawal's own recommended 1.3 design. Close to replication, with a new fixed-FPR protocol. That is methods, and worth having.

**Judge.** "Your detector fires on shared priors and you calibrated it to ignore them." Pre-empt with an operating characteristic at 1/5/10% FPR on both nulls, plus a seeded ρ injection.

**Verdict: KEEP.** Two nulls and the injection; a well-powered null here is itself a result.

## H1 — Three standards

**Feasibility.** Cheapest, and mostly no new runs — except case (iii), "talk with no behavioural change", which exists in no shipped log. Run it or drop the cell.

**Confound.** Three case types from three environments: disagreement between standards is confounded with task. And the coders wrote the rubric knowing the condition.

**Novelty.** [Berger](https://www.americanbar.org/groups/antitrust_law/resources/magazine/2025-fall/coordination-code-rethinking-antitrust-liability-age-ai-pricing/) already supplies the legal standard and its plus factors; a three-standard taxonomy is a re-description. The novel artefact is a *reproducible* disagreement.

**Judge.** "Your confusion matrix is your own opinion in three columns." Pre-empt twice: score with **published detectors** (price screen, Xu residual correlation, Agrawal's 1–4 judge, Shi claim–action) rather than hand-coding; and add one case where the standards **must** disagree by construction — Xu's scripted comonotone generator (competitive marginals, maximal dependence, no messages). That is a free, CPU-only positive control, which H1 currently lacks.

**Verdict: KEEP, MODIFY.** Detectors instead of coders plus the Xu case; then the most reliable submission available.

## R1 — Dolos

**Feasibility.** 6.2 GB download; CPU generation of 300–500 prompts × 2 models at 1.5B is 3–6 h. Discovery is uncertain (organisers say agents failed in one attempt) and localisation is another day. Structurally, **no positive control is possible** — you do not know the answer — and that is the brief's first criterion.

**Confound.** A 1.5B fine-tune differs on formatting, refusal style and repetition; the README warns differences "do not necessarily reveal the hidden misalignment". "Dolos is more willing to X" is unfalsifiable without a specificity control.

**Novelty.** Not collusion; judged on a separate challenge.

**Judge.** "You found fine-tuning damage." Pre-empt with a specificity ladder — two or three public 1.5B fine-tunes as benign references, plus a dose–response across elicitation strength.

**Verdict: KILL** for a collusion-track team; $0 lottery ticket only, with a hard 10-hour cap.

---

## What the shortlist misses

**1. Leniency bounty on a formed cartel.** Branch a passing `llm-cartel` run; offer *one existing member* privately: report the agreement, keep a 10% margin bonus, your partner is not told. Measure undercutting, reporting, punishment, price recovery. No new harness — `branch_game.py` plus a prompt line — three to five base runs, ~2,000 calls. Beats J1: the cartel already exists (no recruitment problem), the outcome is a price, and it tests the actual antitrust instrument (DOJ/EU leniency), untested on LLM agents.

**2. Monitor–monitor collusion.** Gap 16, listed with no idea attached. Score the same 150–300 shipped trajectories with three judges from different providers and test correlated leniency: does A's leniency predict B's on the same episode, conditional on the behavioural metric? If monitor errors correlate, an ensemble buys nothing. ~600 calls, no new environment, and a headline judges remember.

**3. Detection-power budget.** Use the shipped logs (Agrawal's 75 runs, ColludeBench's 1,737) to estimate between-seed variance for price and dependence, then compute the N each shortlist project needs — L1's 1.5 points, B1's recovery time, J1's acceptance gap — and its dollar cost. Zero API. It beats H1 because it is quantitative and predicts which of the other six can work; run it first and it disciplines the weekend.

**4. Gag-channel capacity.** Treat Agrawal's 5-character cap as a channel and measure its information rate: mutual information between the gagged message and the next-round price move, in bits per round, against the profit sustained. This answers *how many bits a cartel needs* — a Shannon-style bound linking Agrawal's qualitative finding to Tailor's capacity theory. Reuse the 75 shipped runs plus ~20 new gagged runs.

**5. Upward-deviation followership (the price beacon).** A scripted seller raises its ask 10% above the collusive level for three rounds, then reverts; measure whether rivals follow within k rounds, against an equal downward deviation. Following an *unprofitable* upward move is evidence of a norm, not of market structure — the cleanest answer to "is the high price collusion or competition?". One scripted seat, 10 runs × 30 rounds ≈ 600 calls.

## Bottom line

Keep C1 or H1 for a result you can defend; take J1 only as the betrayal study; and run the power budget (missed idea 3) in the first three hours — it tells you which of the other six can work at all.
