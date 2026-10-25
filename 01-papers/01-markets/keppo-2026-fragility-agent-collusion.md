---
id: keppo-2026
title: "On the Fragility of AI Agent Collusion"
authors: ["Jussi Keppo", "Yuze Li", "Gerry Tsoukalas", "Nuo Yuan"]
year: 2026
venue: "arXiv preprint (cs.GT), 18 Mar 2026; 48 pp."
arxiv: "2603.20281"
url: "https://arxiv.org/abs/2603.20281"
code: "none in paper; organisers point to https://github.com/mattriemer/LLMCartel (bundled as llm-cartel/ in the starter repo)"
tracks: ["1.1", "1.2", "1.5"]
role: "core-result"
verification: "full-text"
---

# On the Fragility of AI Agent Collusion (Keppo et al. 2026)

**One-line takeaway.** LLM collusion is fragile to *heterogeneity*, not to capability: patience or data asymmetry cuts price elevation from +22% to +10% / +7%, a Q-learning counterpart prevents sustained collusion outright, a fifth seller stops it within 1,000 periods — but a 32B-vs-14B pair still colludes at +21% by settling into leader–follower roles.

## The question it asks

Fish et al. show symmetric LLM agents collude. Real firms buy different models with different prompts, objectives, data feeds and update cadences. Does LLM collusion survive that heterogeneity, and which dimension matters most?

## Setup

- **Environment / game:** repeated Bertrand oligopoly, N sellers, homogeneous good, multinomial-logit demand (`a=2`, `μ=0.25`, `c=1`, `a0=0`, `δ=0.95`). Static Nash `p^C ≈ $1.47`; joint monopoly `p^M ≈ $1.92`. Demand primitives are never shown to agents. Convergence = 100 consecutive periods with all pairwise price gaps ≤5% of the lowest price, else a 1,000-period cap.
- **Agents & models:** locally-run **DeepSeek-R1-Distill-Qwen-32B**, a **14B** variant, a tabular **Q-learner** (α=0.15, β=0.004, ε-greedy, state = last price pair, pre-trained against another Q-learner), and **GPT-5-mini** for robustness.
- **N agents / rounds / seeds:** 10 conditions × 10 runs, up to 1,000 periods each (~100,000 periods, 2,235 compute hours); 2–5 sellers; GPT-5-mini 5 runs/condition.
- **Communication channel:** none.
- **Information available:** own price, demand and profit; "high-data" agents also see rival price history; prompts carry up to 100 rounds of history plus the agent's previous `<strategy>` plan.

## Method / interventions

One factor at a time: **patience** as the prompt-specified horizon (δ=0.95 vs δ=0); **data access** (rival history visible or not); **algorithm type** (LLM vs frozen/adaptive Q-learner); **number of sellers** (2→5); **model size** (32B vs 14B); and a closed-source replication with an explicit anti-collusion prompt.

## Key findings (with numbers)

- **Benchmarks:** two patient agents **+22%** ($1.801, SD 0.027) after **195.1 rounds** (SD 28.8), 10/10 runs; two myopic agents **≈0%** ($1.472, 159.0 rounds).
- **Patience heterogeneity:** **+10%** ($1.619, 140.8 rounds; p<0.00001 vs patient–patient).
- **Data-access heterogeneity:** **+7%** ($1.576, SD 0.007; 151.2 rounds; p<0.00001), ≈12.5% below the symmetric-information baseline.
- **Cross-algorithm:** LLM vs Q-learner never converged in any of 10 runs (frozen **+2%**, $1.506; adaptive **+8%**, $1.583); all hit the 1,000-period cap.
- **Number of sellers:** 3 → **+36%** ($2.000, 208.3 rounds); 4 → **+11%** ($1.632, 542.1); 5 → **+3%** ($1.514), no convergence.
- **Model size:** 32B vs 14B **+21%** ($1.775, 458.4 rounds) — level intact, convergence 2.3× slower. The 32B anchors: 97 mentions of price-war avoidance before round 345, $1.82 with 48 price changes while the 14B averaged $1.89 over 83 moves; from round 249 the 14B holds $1.80–1.85 and the 32B undercuts at $1.75.
- **GPT-5-mini:** patient–patient **+57%** ($2.312); myopic–myopic **−29%** ($1.046); patient/myopic +36%; high/low-data +42%.
- **Anti-collusion prompt (GPT-5-mini only, 5 runs):** patient–patient **−29%** ($1.044), near marginal cost ≈$1.03–1.05; every anti-collusion cell between −30% and −2%.
- **Sanity:** one-shot monopoly and Nash recovered within 5%; repeated monopoly price learned within 1%.

## Mechanism / why it happens

Patience asymmetry removes the impatient agent's incentive to sustain punishment, so the patient agent cannot credibly threaten retaliation. A data-poor seller cannot detect deviations, hence cannot punish, and the data-rich seller exploits by undercutting. Q-learners cannot parse the LLM's cooperative pricing pattern, so coordination never stabilises. More sellers raise strategic uncertainty (chain-of-thought moves from confident coordination to caution to defensiveness), while size asymmetry supplies a **focal role assignment**. Alternative explanation worth testing: the 32B/14B result may reflect a shared prompt template and tokenizer family rather than a general leader–follower effect.

## Limitations and threats to validity

10 runs per condition (directional patterns, not marginal effects); one open model family plus GPT-5-mini; black-box mechanism; a single MNL parameterisation; the 1,000-period cap censors "no convergence" cells; patience is a prompt, not a computed discount factor; no communication channel.

## Relevance to the sprint

- **Q1.1** — two clean single-variable levers with measured effect sizes: horizon/patience and rival-price visibility.
- **Q1.2** — the Q-learner arm is the strongest evidence that *architecture* mismatch dissolves collusion while size mismatch does not; no mid-run replacement is tested.
- **Q1.5** — "algorithmic diversity" is priced as a restriction: it removes collusion but also removes coordination.

## Project hooks (48-hour sized)

1. **Q-learner swap-in on a live cartel.** Positive control: two same-model API agents in a 300-round Bertrand duopoly crossing +15% elevation by round 300 (2–3 seeds). Intervention: branch the saved transcript and replace seller 2 with a frozen Q-table (or a scripted ε-greedy best-response on a 20-point grid). Metric: mean elevation over the last 100 rounds plus rounds-to-recover; cost $30–80.
2. **History-length gradient.** Same harness; show one seller 0 / 10 / 100 rounds of rival price history. Positive control: 100 rounds reproduces elevation >15%; metric: elevation and convergence round; cost ≈$20–60.
3. **Cross-provider leader–follower probe.** Pair a strong and a weak model from *different* providers; metric: rank correlation between the stronger model's price and the eventual corridor; cost ≈$40–100.

## What this paper does NOT test

Mid-run replacement of a colluding participant; explicit or covert channels; temperature effects; cross-provider pairs; liability schemes; detection from trajectories; more than one demand system.

## Related notes in this folder

- `eschenbaum-2022-robust-algorithmic-collusion.md` — Q-learning version of the replacement question; why a Q-learner partner breaks an LLM cartel.
- `collina-2025-breaking-algorithmic-collusion.md` — theory for a single non-equilibrium participant.
- `dhanda-2026-price-cap-collusion.md`, `bracale-2026-institutional-ai-governance.md` — prompt interventions with very different effect sizes.
- `fish-2024-algorithmic-collusion-llms.md` — the symmetric baseline this paper perturbs.

## Verification log

- Read: abstract page `https://arxiv.org/abs/2603.20281` **and** arXiv HTML v1 full text `https://arxiv.org/html/2603.20281v1` (§1–§7.2, Tables 1, 3, 4, 5, 6).
- Numbers spot-checked: yes — Tables 5 and 6 cross-checked against §4–§6 prose and figure captions.
- Could not confirm: decoding temperature (not stated in sections read); "over 2,000 compute hours" in the abstract vs 2,235 in Table 4; exact anti-collusion prompt wording.
