---
id: fish-2024
title: "Algorithmic Collusion by Large Language Models"
authors: ["Sara Fish", "Yannai A. Gonczarowski", "Ran I. Shorrer"]
year: 2024
venue: "ACM EC 2026 (accepted); arXiv v6, 31 Aug 2026"
arxiv: "2404.00806"
url: "https://arxiv.org/abs/2404.00806"
code: "https://github.com/luciasauer/algorithmic_pricing_llms (independent reimplementation used by the starter repo)"
tracks: ["1.1", "2.1", "3.1"]
role: "core-result"
verification: "full-text"
---

# Algorithmic Collusion by LLMs (Fish, Gonczarowski & Shorrer)

**One-line takeaway.** Two off-the-shelf LLM pricing agents, told only to maximise long-run profit and unable to talk, reliably reach supracompetitive prices within a few dozen periods — and rewording a few innocuous lines of the prompt moves prices toward or away from the monopoly benchmark.

## The question it asks
Can generative AI agents — which need no training period and no explicit pricing rule — autonomously produce collusive-like outcomes? And if so, what in their reasoning drives it?

## Setup
- **Environment.** Repeated Bertrand oligopoly with logit demand, following Calvano et al. (2020). One run = **300 periods**. Each period every firm sets a price; demand and profit are realised; each agent then sees **all prices, its own demand and its own profit**. Agents are *not* given the demand function.
- **Agents.** One LLM per firm, instructed in lay terms to maximise the firm's long-term profit. Nothing in the prompt suggests collusion, retaliation, or that the competitor is an LLM. **No communication channel** other than observed prices.
- **Models.** GPT-4 family in the main experiments; robustness with GPT-5.2 at high reasoning effort (v6).
- **Agent architecture.** A prompt containing instructions, market history, and a persistent **"plans and insights"** scratchpad the agent writes for itself across periods.
- **Prompt prefixes.** The experiment varies only the last few lines of the opening instruction — e.g. a prefix that reiterates long-term profit versus one that mentions the option of selling more by lowering price.

## Method / interventions
1. **Duopoly baseline:** do prices exceed the static Bertrand–Nash benchmark?
2. **Prompt-prefix comparison:** same economics, different innocuous wording.
3. **Reward–punishment analysis:** regress each agent's price on the competitor's recent prices to recover a response scheme (on-path) and estimate punishment intensity.
4. **"Implantation" (novel):** reset a run to a chosen period, replace the agent's just-written reasoning with reasoning from another session that argues for avoiding a price war, and continue. This is a *causal* intervention on the agent's text, not just a correlation.
5. **Robustness:** stochastic demand, asymmetric firms, heterogeneous pricing agents, discounting instructions, newer model, and a first-price auction setting.

## Key findings
- LLM duopolists **quickly and consistently** reach prices and profits significantly above the one-shot Bertrand–Nash equilibrium, with no collusive instruction and no communication.
- The profit-maximising prompt prefix produces profits **close to the monopoly benchmark** (both firms pricing as one monopolist would). A one-line difference in wording is enough to move the market between "high" and "very high" supracompetitive outcomes.
- **Price-war fear is a cause, not just a correlate.** Implanting price-war-avoidant reasoning raises subsequent prices substantially.
- On-path behaviour is consistent with a **reward–punishment scheme**: a low competitor price is met with lower prices over several periods with decaying intensity; the high-price prompt prefix produces a *steeper* punishment scheme.
- Text clustering shows the high-price prefix shifts reasoning toward **maintaining price levels and reacting to the competitor**; the lower-price prefix shifts it toward **undercutting and exploration**.
- Results **extend to first-price auctions** and survive noise, asymmetry, heterogeneous agents, discounting, and a much newer model.

## Mechanism / why it happens
The authors' account: LLMs arrive with a prior that price competition is destructive ("price wars are bad for business"), so they avoid undercutting and retaliate gently when undercut. That prior, plus in-context learning from the price history, is enough to sustain a reward–punishment equilibrium — no explicit agreement. Alternative readings worth testing: the model may simply be imitating textbook oligopoly behaviour, or anchoring on a salient price; the paper's implantation result makes pure imitation a weaker explanation but does not rule out anchoring.

## Limitations and threats to validity
- **Two firms only** in the main design; no entry, no capacity, no product differentiation beyond logit.
- **One economic environment** (logit Bertrand), one demand parametrisation per run, 300 periods — long enough that "quickly" still means tens of periods.
- **No communication**, so this is tacit collusion by price signalling only; it says nothing about chat channels.
- Prompt sensitivity cuts both ways: the result is robust in sign but the *level* is fragile to wording, which makes cross-paper comparisons of "collusion rates" hazardous.
- "Collusion" is defined by **outcomes plus inferred punishment**, not intent or agreement. Legally this is parallel conduct, not a cartel.
- Main experiments are OpenAI models; the v6 robustness check with GPT-5.2 is reassuring but the paper does not test open-weight or cross-provider pairs.

## Relevance to the sprint
- **Q1.1** — the canonical positive control for market collusion; also the clearest demonstration that *prompt wording* is a causal lever. Any 1.1 project should reproduce this before ablating anything.
- **Q2.1** — shows a market task with no explicit collusion prompt is sufficient; useful as the "market" pole when contrasting with workplace tasks.
- **Q3.1** — collusion is carried by the **public price history alone**; no text channel exists. This is the cleanest existing example of an action-only carrier.
- **Q2.3** — the paper's evidence standard is outcome-based (supracompetitive prices + estimated punishment). It is a good foil for "plus factor" thinking: high prices alone are not an agreement.

## Project hooks (48-hour sized)
1. **Visible-history ablation.** Replication of the high-price duopoly, then vary the number of past periods shown (0 / 10 / 100 / full). Positive control: mean price above Nash in the full-history arm. Metric: mean price, price dispersion, estimated punishment coefficient. This is the starter repo's own 1.1 project; cheap and low-risk.
2. **Prompt-prefix dose–response.** Take 6–8 innocuous prefixes (including Dhanda's price-cap framing and a "compete aggressively" framing) and run 5 seeds each. Metric: distance of mean price from Nash and from the monopoly benchmark. The interesting result is a *ranking of wording*, not a single number.
3. **Scratchpad ablation.** Run with the persistent "plans and insights" notes on/off and with notes visible vs. private. Does the collusive equilibrium need the agent's own written memory, or does in-context price history suffice? Metric: periods-to-threshold and price level.

## What this paper does NOT test
Replacement of a participant mid-run; more than two firms; cross-provider pairs; communication; monitoring/oversight; whether agents *recognise* each other; whether the behaviour survives a change of harness or prompt template.

## Related notes in this folder
- `keppo-2026-fragility-agent-collusion.md` — adds firms, heterogeneity and Q-learners; the main fragility counterweight.
- `collina-2025-breaking-algorithmic-collusion.md` — no-regret participant as a destabiliser.
- `../01-markets/agrawal-2025-double-auction.md` — communication and oversight in a richer market.
- `../02-detection/aharon-2026-focal-points-coordination.md` — benign Schelling-point coordination, the "no-agreement" control.

## Verification log
- Read: abstract page and HTML full text v6 (https://arxiv.org/html/2404.00806v6), sections 1–2 and the results summary; later sections truncated by the fetch.
- Numbers spot-checked: 300 periods, "close to monopoly" framing, GPT-5.2 robustness, first-price auction extension — all confirmed in the fetched text.
- Not confirmed: exact mean prices/profit levels (they are in figures/tables beyond the fetched truncation), exact number of prompt prefixes, exact GPT-4 version. Do not quote a specific price level from this note.
