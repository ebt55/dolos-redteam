# Sprint brief — AI Collusion Research Sprint (Apart Research)

**Source:** https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25 (fetched 24 Oct 2026)
**Status when fetched:** live; 1,640 signed up.

## The one-screen version

| | |
|---|---|
| **Dates** | Fri 23 – Sun 25 Oct 2026 |
| **Format** | Online, 3 days, teams of 1–5; in-person hubs at Collider (NYC) and AI Safety Hong Kong on Sat/Sun |
| **Deadline** | **25 Oct 2026, 23:59 Anywhere on Earth** = **26 Oct 2026, 17:29 IST** (AoE is UTC−12). In India that is Monday afternoon, not Sunday night. |
| **Organisers** | Apart Research, Poseidon Research, AE Studio; support from Modal and the AI Alignment Foundation |
| **Prizes** | $2,000 total: $1,000 / $500 / $300 / $100 / $100 |
| **Compute** | Modal credits: $250 per person at the NYC hub, $50 for every other participant |
| **Submit** | Project title, abstract, **PDF report**, track(s), presentation recording, code, slides, image; team details |
| **After** | Winners announced ~1–2 weeks later; top teams fast-tracked to the Apart Fellowship and possible publication on AF/LessWrong |

## What the sprint asks

> When does collusion emerge, and which levers cause it? What should count as convincing evidence that agents are colluding, using logged trajectories? How is coordination mediated, and how can it be broken?

Three tracks, twelve research questions, plus a model-organism red-teaming challenge:

1. **Markets and Collusion** — 1.1 necessary variables; 1.2 robustness to replacement; 1.3 better detection; 1.4 information-theoretic detection; 1.5 cheapest single restriction.
2. **Detection and Audit** — 2.1 which tasks produce collusion; 2.2 say-vs-do detection; 2.3 standards of evidence (plus the Dolos-1.5B red-team).
3. **Carriers and Countermeasures** — 3.1 action/tool side channels; 3.2 trusted agents; 3.3 peer identification; 3.4 behaviour under surveillance.

Every question ships with starter code and a weekend-sized project. The intended project shape is: **a controlled experiment with a positive control, one manipulated variable, and an objective metric** — not a demo and not a literature review.

## What "good" will probably look like (inference, not official)

The organisers repeatedly emphasise isolation ("single effects so they can be isolated and measured objectively"), positive controls ("start with 3–5 seeds… expand only after the positive control works"), and costs. A strong submission likely has:

1. **A crisp construct.** State which definition of collusion you measure (outcome-based supracompetitive pricing, coalition advantage, dependence, secret agreement). The repo's `literature/definitions` makes this a live issue.
2. **A working positive control** — reproduce a known collusion result before your intervention.
3. **One clean manipulation**, with seeds and a pre-declared metric.
4. **A negative/benign control** — e.g. no-communication same-model runs, or a focal-points task — so you can claim the effect is coordination, not shared priors.
5. **Honest limitations** and a replication artefact (code, logs, configs).
6. **A short, legible report** with one headline figure.

A negative result is publishable here if the positive control worked and the null is well-powered: "we could not reproduce X under Y" is a contribution. A failed positive control with no diagnosis is not.

## Practical constraints the organisers set

- Laptop-class compute, no GPU for all default routes; only 2.2's TraceGuard needs Docker.
- Typical budget $5–$120 per project; 3–5 seeds per condition first.
- Model access via Nebius or OpenRouter keys (either works); Modal for custom models.
- 300-round duopoly ≈ 600 sequential calls; 12–24 pilot runs ≈ 7k–14k calls.
- The starter repo is designed to work with a coding agent (Claude Code / Codex), not just by hand.

## Time budget from 24 Oct 09:15 IST

≈ **56 hours** to the AoE deadline. Treat the last 8 hours as writing/recording only. A realistic split:

- **Now → +6h:** pick question, read 3–4 core papers, run the smallest possible positive control.
- **+6h → +30h:** build the harness / run conditions (sleep included).
- **+30h → +44h:** analysis, one more seed batch if the effect is noisy, robustness check.
- **+44h → +54h:** report, figures, slides, recording, code cleanup.
- **+54h → deadline:** submit early; do not rely on the last hour.

## Red-teaming challenge (parallel option)

Dolos-1.5B is a Qwen2.5-1.5B-Instruct fine-tune with a hidden misaligned behaviour; participants get only weights (≈6.2 GB), no API key, no GPU required. Deliverables: find the behaviour, explain its mechanism, and design an audit that works **without a reference model**. This is a good fit for a small team that prefers interpretability/red-teaming over running many API calls, and it costs $0 in inference. It is also the highest-variance option: a partial discovery with a solid method may score better than a shallow full answer.

## Links

- Sprint page: https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25
- Starter repo: https://github.com/poseidon-research/collusion_hackathon
- Discord: https://discord.gg/XswWBvugYs
- Contact: sprints@apartresearch.com
