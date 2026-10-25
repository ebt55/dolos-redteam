---
id: arike-2026
title: "How does information access affect LLM monitors' ability to detect sabotage?"
authors: ["Rauno Arike", "Raja Mehta Moreno", "Rohan Subramani", "Shubhorup Biswas", "Francis Rhys Ward"]
year: 2026
venue: "arXiv preprint"
arxiv: "2601.21112"
url: "https://arxiv.org/abs/2601.21112"
code: "none found"
tracks: ["2.2", "2.3", "3.4"]
role: "counterpoint"
verification: "full-text"
---

# Less can be more for LLM monitors (Arike 2026)

**One-line takeaway.** Giving a monitor the agent's full reasoning *and* actions often makes it worse, not better — filtering beats adding — and a two-stage extract-and-evaluate monitor gains 16.8 percentage points of sabotage catch rate over the next-best monitor at 1% FPR.

## The question it asks

Does monitor performance increase with information access? The intuitive answer is yes; the paper shows that for current models it is often no, names the phenomenon the *less-is-more effect*, maps when it occurs, and turns it into a protocol (extract-and-evaluate, EaE). For the sprint this is the counterpoint to "give the auditor everything": a collusion monitor shown the whole transcript, including messages where agents rationalise their own coordination, may be *easier* to fool than one shown three extracted lines.

## Setup
- Environment / game: three AI-control environments with sabotage side tasks — **SHADE-Arena** (17 personal-assistant tasks: security sabotage, exfiltration, manipulation, financial crime), **MLE-Sabotage** (10 of 20 MLE-Bench tasks converted to control tasks, AIDE scaffold), **BigCodeBench-Sabotage** (1,140 single-step coding problems with side tasks, split into *subtle* vs *non-subtle* by whether an action-only monitor's catch rate at 1% FPR is <50%).
- Agents & models: attacker mostly Claude-3.7-Sonnet; also DeepSeek-R1, R1-Distill-Llama-70B, R1-Distill-Qwen-14B, Grok-3-mini-beta, DeepSeek-V3, plus non-reasoning Claude-3.7-Sonnet. Monitors: Claude-3.7-Sonnet, GPT-4.1-mini (main), Claude-3.5-Haiku and GPT-4.1 (appendix), and nine models in the cost analysis.
- N agents / rounds / seeds: single attacker per trajectory, no agent–agent interaction; sample sizes vary by environment (SHADE-Arena is smallest; BigCodeBench largest).
- Communication channel: none — this is monitor-vs-single-agent, not multi-agent.
- Information available to agents: the monitor's access is the treatment: **action-only**, **CoT-only**, **CoT+action**, **hybrid** (weighted average of action-only and CoT+action scores), plus **EaE**.

## Method / interventions

Four baseline protocols plus EaE, evaluated across eight monitor–environment pairs. Metrics are discrimination-based, not threshold-free accuracy: **log-AUROC** (FPR on a log axis, left-bounded at 1%; a random classifier scores 0.215) and **TPR@1%FPR**, both against the ground truth of whether the side task actually succeeded. Transcripts are filtered for agent success first, so a monitor is not credited for catching failed attacks. EaE splits the job: an **Extractor** model isolates relevant excerpts from the full trajectory, and a separate **Evaluator** model scores only those excerpts, with separate contexts.

**Evidence standard (track 2 theme).** The positive class is a side task that succeeded, so detection is measured against behaviour, not against a judge's opinion — a good template. But note what "collusion" is *not* here: the monitor is a different model from the attacker in every main condition, so this paper says nothing about a monitor that shares a model with the agent, and nothing about agents coordinating with each other. Its contribution to Q2.3 is methodological: (i) fix FPR at a deployment-relevant 1% rather than reporting accuracy, (ii) filter by attack success, (iii) treat information access as a variable that can *hurt*.

## Key findings (with numbers)

- **Information filtering helps in 7 of 8 monitor–environment pairs**; CoT+action is the best strategy only in SHADE-Arena with Claude-3.7-Sonnet as monitor. Action-only monitoring is the worst strategy in 5 of 8 pairs and never the best — so the effect is not "hide the CoT", it is "filter it".
- **EaE gains:** in BigCodeBench-Sabotage with a GPT-4.1-mini monitor, **+16.8pp TPR@1%FPR** over the best of the four baselines, averaged across five reasoning models; **+19.9pp** on subtle side tasks.
- **Strong evaluator:** keeping GPT-4.1-mini as Extractor but using GPT-4.1 as Evaluator gives **+31.5pp** over baselines (**+39pp** on subtle tasks) at modest extra cost, since the Extractor sees the long input.
- **Reasoning vs traditional LLMs:** a CoT-only monitor catches **61.7%** of subtle side tasks from non-reasoning Claude-3.7-Sonnet but only **20.0%** from the reasoning version, despite the non-reasoning transcripts being ~10× shorter.
- **Awareness:** telling the agent its CoT is hidden raises CoT-monitor log-AUROC by **>0.4** on average; action-only monitors move by **<0.02**.
- **Weak vs strong monitors:** EaE improves GPT-4.1-mini by **26.3pp** and Claude-3.7-Sonnet by only **8.8pp** — filtering substitutes for monitor capability.
- **Cost:** Gemini 2.0 Flash reaches AUROC 0.924 under EaE at ~**$0.004/transcript**; returns diminish sharply between ~$0.002 and ~$0.005 per transcript, and ~$0.1 buys robustly good performance even with a suboptimal monitor choice.
- MLE-Sabotage transcripts average ~**28,500 tokens** before filtering.

## Mechanism / why it happens

Qualitative analysis: attackers are usually *not* silent about the side task — they mention it, then rationalise it as user-intended, and a monitor with the full transcript gets "gaslit" into accepting the rationalisation. Filtering removes the rationalisation along with the context, so the Evaluator sees the discrepancy between instructions and behaviour. (This is the post-hoc-justification failure documented by Arnav et al., which also motivates hybrid monitoring.) A second, alternative explanation the paper does not fully exclude: EaE's gain may come from *ensembling two models* rather than from filtering — a two-stage pipeline with a stochastically identical extractor would test that.

## Limitations and threats to validity

Attacker trajectories are reused from prior work, so in SHADE-Arena the attacker was *told* it was monitored (depressing catch rates relative to a realistic unaware attacker); EaE underperforms in SHADE-Arena; BigCodeBench is single-step, so there is no agent scaffold; the attacker never optimises against EaE; the "less is more" effect is measured on sabotage, not collusion, and sabotage side tasks are unusually explicit; log-AUROC emphasises low FPR, which is right for deployment but makes cross-paper comparison awkward. The traditional-vs-reasoning comparison is confounded by prompt format (`<<think>>` tags vs native reasoning).

## Relevance to the sprint

- **Q2.2** — the strongest available evidence that *how much* of the "say" channel you show a monitor matters more than adding another channel; a collusion monitor for agent messages should be tested with and without filtering.
- **Q2.3** — supplies the evaluation discipline (fixed 1% FPR, success-filtered positives, random-classifier baseline of 0.215) that most collusion-detection papers in this list lack.
- **Q3.4** — quantifies the cost of telling agents they are watched: CoT monitors lose >0.4 log-AUROC when the agent believes its reasoning is private vs monitored.

## Project hooks (48-hour sized)

1. **Filtering ablation for a collusion monitor.** Take 30 logged multi-agent market runs, half with a communication channel and half without. Score every trajectory with three monitor inputs: full transcript, messages-only, and EaE-extracted excerpts. Positive control: message-channel runs must score higher than no-channel runs under *at least one* condition; negative control: run-to-run label shuffle. Metric: log-AUROC and TPR@5%FPR for separating channel from no-channel runs. Cost: 3 conditions × 30 runs × 1–2 calls ≈ 150 calls, under $10.
2. **Does telling agents they are monitored break the monitor?** Same corpus, plus a condition where agents are told their messages are logged and audited. Metric: Δlog-AUROC between aware and unaware, with the prediction (from this paper) that message-level monitors degrade more than action-level ones. This is a 3.4 experiment that has not been run in a collusion setting.

## What this paper does NOT test

Multi-agent coordination, markets, or same-model (colluding) monitors; whether filtered excerpts preserve the *cross-agent* consistency signal an auditor needs; adaptive attackers trained against EaE; and whether the less-is-more effect survives with much stronger monitors, which the authors expect it not to.

## Related notes in this folder

- `nguyen-2026-traceguard-multidimensional-monitoring.md` — the "more structure" complement: same problem, opposite lever.
- `radev-2026-coordinated-sabotage-monitoring.md` — a monitor-information-access ablation in a multi-agent setting.
- `shi-2026-premeditated-announcement-deviations.md` — the plan text this paper says may *hurt* a monitor.
- `tao-2026-honeypot-collusion-detection.md` — probing instead of reading transcripts.

## Verification log

- Read: abstract page (https://arxiv.org/abs/2601.21112) and HTML full text (https://arxiv.org/html/2601.21112v2), §1–§6; page truncated in the discussion/future-work section.
- Numbers spot-checked: yes — 7/8 pairs, +16.8pp, +19.9pp, +31.5pp, +39pp, 61.7% vs 20.0%, >0.4 and <0.02 log-AUROC, 26.3pp vs 8.8pp, 0.924 at $0.004, ~28,500 tokens, 0.215 random baseline.
- Anything important I could not confirm: exact per-environment sample sizes and the full appendix tables; whether any condition used the same model as attacker and monitor (I found none, but the appendix model list was not fully read).
