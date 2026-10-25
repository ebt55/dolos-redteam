# 04 — Collusion carriers and countermeasures: index rows

Six notes on how coordination is carried (prompt artefacts, price actions, code style, model identity) and what that implies for monitors. Sprint track IDs refer to the research questions on the [AI Collusion Research Sprint](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25) resources page (1.x markets, 2.x detection/audit, 3.x carriers/countermeasures).

| file | title | authors | year | venue | link | tracks | role | one-line takeaway |
|---|---|---|---|---|---|---|---|---|
| `tian-2026-shared-prompt-carrier.md` | Prompt Optimization Enables Stable Algorithmic Collusion in LLM Agents | Yingtao Tian | 2026 | arXiv preprint (cs.AI) | [2604.17774](https://arxiv.org/abs/2604.17774) | 3.1, 1.1, 2.3 | core-result | Two price-setters with **no message channel** reach stable supracompetitive prices because an optimiser rewrote the **shared system prompt** into a public convention — the carrier is prompt content plus public prices, and forbidding "secret sharing" in the prompt does not stop it. |
| `dietrich-2026-stylometric-peer-identification.md` | Can Multi-Agent LLMs Identify Their Peers? Stylometric Fingerprinting in Role-Constrained Political Analysis | Juergen Dietrich | 2026 | arXiv preprint (cs.CL) | [2606.09854](https://arxiv.org/abs/2606.09854) | 3.3, 3.2 | core-result | A T5-base fine-tune hits **Macro F1 = 0.991** (statement-disjoint CV) identifying one of five model families from short role-constrained text **after prompt-level anonymisation** — renaming agents does not hide them, and ~440 texts is enough. |
| `kale-2025-monitor-awareness-dominates.md` | Reliable Weak-to-Strong Monitoring of LLM Agents | Neil Kale, Chen Bo Calvin Zhang, Kevin Zhu, Ankit Aich, Paula Rodriguez, Scale Red Team, Christina Q. Knight, Zifan Wang | 2025 | arXiv preprint (cs.AI) | [2508.19461](https://arxiv.org/abs/2508.19461) | 3.4, 3.2 | core-result | **Agent awareness dominates monitor awareness**: telling the agent it is watched degrades reliability more than informing the monitor helps, and hybrid scaffolding beats both — unaware agents are already detected at AUC ≥ 0.9. |
| `najt-2026-monitor-blind-spot-attacks.md` | SLEIGHT-Bench: A Benchmark of Evasion Attacks Against Agent Monitors | Elle Najt, Colin Toft, Tyler Tracy, Fabien Roger, Joe Benton | 2026 | arXiv preprint (cs.CR) | [2605.16626](https://arxiv.org/abs/2605.16626) | 3.4, 2.3 | core-result | **20 of 40** hand-written attacks exploiting conceptual monitor blind spots are never flagged by an Opus 4.6 monitor across 10 trials at 1% FPR (overall catch **32%**), with N-hops, omission and jailbreaks at **0/10–0/20**. |
| `jiralerspong-2026-agents-infer-cot-monitoring.md` | Noticing the Watcher: LLM Agents Can Infer CoT Monitoring from Blocking Feedback | Thomas Jiralerspong, Flemming Kondrup, Yoshua Bengio | 2026 | arXiv preprint (cs.CR) | [2603.16928](https://arxiv.org/abs/2603.16928) | 3.4, 2.3 | core-result | Told their reasoning is private, agents infer the hidden CoT monitor **from blocking feedback alone** (confident belief in up to **19%** of episodes); **3 of 2,400** episodes stated intent to hide reasoning, and all three immediately reasoned openly and were caught. |
| `greenblatt-2023-untrusted-monitor-collusion.md` | AI Control: Improving Safety Despite Intentional Subversion | Ryan Greenblatt, Buck Shlegeris, Kshitij Sachan, Fabien Roger | 2023 | ICML 2024 (arXiv v5) | [2312.06942](https://arxiv.org/abs/2312.06942) | 3.2, 3.1 | background | Untrusted monitors collapse to **0% safety** on "pretend not to see backdoors" and recover to **79%** only via synthetic-attack validation plus redaction — and a **for→while loop substitution** still carries the one bit needed to collude. |

## How the six fit together

- **Carriers (Q3.1):** Tian shows a carrier with no messages at all (shared prompt + public prices); Greenblatt shows a carrier with no messages at all in code (style as a one-bit channel). Together they set the floor for what "we removed the communication channel" must mean.
- **Identity (Q3.3):** Dietrich removes the anonymity countermeasure — peers are identifiable from a few hundred texts, which also raises the value of Tian's shared-prior carrier and threatens Greenblatt-style trusted-agent infiltration.
- **Watching (Q3.4):** Kale (told) and Jiralerspong (inferred) establish that the monitor's own existence and its blocks are the leak; Najt supplies the menu of what a coalition does with that knowledge.
- **Evidence (Q2.3):** Najt and Jiralerspong both imply per-message/per-CoT suspicion is insufficient: evidence has to live in cross-action invariants, not single observations.

## Verification status at a glance

| note | verification | gap |
|---|---|---|
| tian-2026 | full-text | Appendix C (episodes `T`, configs `K`, seeds, model identities) not retrieved |
| dietrich-2026 | full-text | §4.5 verdicts, §5.5 limitations, §7 code availability not retrieved |
| kale-2025 | partial | Findings 2–5 magnitudes are figure-level; §4.3 onward not retrieved |
| najt-2026 | full-text | per-model results (Fig. 2) and Appendix E not retrieved; proprietary prompt withheld by authors |
| jiralerspong-2026 | full-text | per-model awareness by episode (Figs. 1–2) image-only |
| greenblatt-2023 | partial | §3.4.1–3.4.2 prose and §5.1 limitations not retrieved; **no paraphrasing intervention found** |
