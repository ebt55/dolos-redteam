# Post-list prior art — the two papers v1 missed

This page exists because the first shortlist did what most sprint prep does: it checked the organisers’ list, the cited papers, and a few adjacent works, but it did **not** sweep for papers published after the list was assembled. Two of those papers cover v1’s top two projects. The correction is in `../04-ideas/FINAL-SHORTLIST.md` v2.

## 1. Tran & Yu 2026 — the downward forced-deviation audit

**Citation:** Hieu Tran & Hong Yu, *Is Anyone Enforcing the Cartel? What Reinforcement Learning Teaches LLM Agents in Markets*, arXiv:2610.28787, submitted **20 October 2026** (45 pages).

**What it does.** It introduces an audit that tests enforcement by **forcing a cartel member to cheat in counterfactual copies of a market**. It studies RL-trained small LLMs in pricing and trading, and prompted LLMs. Headline findings:

- Small RL agents learn what their training rivals reward, but only what they readily try.
- Against a punishing rival they learn to be deterred; against a cheating rival they match cuts, not the costly price war that would deter.
- Against their own copies, deterred and matching agents can earn the same cartel profits, but only matching ones enforce, and then thinly.
- **Prompted LLMs reach cartel-like outcomes mostly through rules that ignore the market. Outcome measures cannot tell these cases apart; the audit can.**

**Why it matters for v1.** v1’s #1, D1, proposed exactly this: a scripted price cut in a collusive vs competitive market, measuring punishment. The **downward** arm is a replication. The **upward** arm — does a rival follow a price rise? — is not what Tran & Yu test; that survives as **BEACON**. v1 also said “we found no published application to LLM agents as an audit; search once before claiming novelty.” That sentence was false on 24 October.

**What v2 does.** D1 becomes **BEACON**: upward-only primary, downward arm explicitly labelled a replication of Tran & Yu, with the citation burden acknowledged.

## 2. Lee 2026 — the leniency experiment

**Citation:** Lee 2026, SSRN 7426061. The SSRN page returned **HTTP 403** to automated fetches, so this is a **pack claim**, not a paper read here.

**What it reports (per the other pack).** A repeated pricing duopoly with LLM firms, cheap talk, and an LLM competition authority. Leniency plus a reward raises **reporting**, but prices barely move (9.81 → 8.88 in the pack’s reading), the cartel keeps ~98% of the markup, and there is **no retaliation**.

**Why it matters for v1.** v1’s #2, L2, proposed a private leniency offer to one cartel member and measured reporting, undercutting, and partner punishment. Lee already answers the main question. The residual — a private single-member offer in N ≥ 3 — is incremental, and v1’s no-offer control assumes a formed cartel that the shipped harness does not reliably produce.

**What v2 does.** L2 is **dropped**. If you want a leniency paper, the only defensible version is a private offer in a larger market with a formed cartel, and you must cite Lee and explain the increment.

## 3. The sprint-repo census

The other pack searched ~60 public GitHub repositories from this sprint (dated 23–24 October) and found concurrent work on:

- **Undercover/agent-delivered offers** — three teams; this is why v1’s G falls out of the top five.
- **Dependence detectors / plus-factor rules** — several; this is why v1’s C1 is not novel.
- **Replacement / peer swaps** — several; this is why B1 is dead.
- **Collusion probes** — at least one; this is why a probe project needs a reference-free audit and a specificity ladder.
- **Message-cap / partial monitoring** — several; this is why CAP is weak.

The census is the other pack’s claim, not independently re-run here. The lesson is what matters: **the sprint itself is a source of prior art.** A shortlist that ignores the other teams will recommend work that is already being done next door.

## 4. What v1 got wrong, and why

| v1 claim | Reality | Consequence |
|---|---|---|
| D1: “no published application to LLM agents as an audit” | Tran & Yu, 20 Oct 2026 | D1 is half-scooped; only upward BEACON survives |
| L2: “No LLM paper tests it” | Lee 2026 (pack claim) | L2 is fully scooped |
| C1: “calibrated dependence audit” | Xu/Agrawal 2×2 already; sprint repo pre-registered it; negative pilot (AUC 0.53) | Drop or reframe as a negative |
| G: “the sprint says untested” | Three sprint teams running it; Zeng acceptance at ceiling | Drop from top five; betrayal-only at best |
| P1/W1/M1 as separate projects | Thinner versions of DISCLOSE/ADVISOR/SELFMON | Merge into the stronger versions |
| H1 as a headline | Berger/KMMW already supply the standard; it is a re-description | Fallback, not headline |

The root cause is **process**, not effort: v1’s prior-art check was a claim audit of the organisers’ list plus a cross-check against one other study. It was not a fresh sweep of arXiv/SSRN/ICML/EMNLP and public sprint repos for work published **after** the list. The other pack did that sweep and caught both scoops.

## 5. The checklist v2 uses

Before ranking any project, run all five:

1. **Search arXiv/SSRN/OpenReview** for the exact question and for the mechanism, restricted to the last 60 days. Use multiple phrasings; the paper may not use your words.
2. **Search GitHub** for the sprint’s public repos and for the broader topic; sort by created/updated date. A repo with a result is prior art even without a paper.
3. **Check the sprint’s own project pages and Discord** (if accessible) for teams doing the same thing. Crowding is not a scoop, but it changes the expected score.
4. **Run a $0 pilot on shipped data** if the project can be tested without new model calls. A negative pilot is better than a clever design.
5. **Write the novelty verdict as a sentence**, not a score: “X is new because no paper/repo tests Y; closest is Z, which does W but not V.” If you cannot write it, the project is not ready.

## 6. Where this leaves the shortlist

- **#1 DISCLOSE** — open after the sweep; closest are Dhanda (announced caps), Anto & Vazquez (qualitative threshold-tracking), and `llmarket` (third-party announced/hidden caps). The disclosure ladder, soft screen, anchoring control and fine-adjusted benchmark are new.
- **#2 BEACON** — upward-only forced deviation; Tran & Yu cover the downward arm.
- **#3 SELFMON** — family leniency on collusion transcripts; prior work conflicts, but none covers this domain.
- **#4 ADVISOR** — repeated market with pooled current data and a firewall; a one-shot sprint team has the same-advisor result.
- **#5 H1** — fallback; the standard is not new.
- **#6 SAYDO** — cross-agent say/do monitor; closest is Radev (monitor sees both but does not cross-reference) and Shi (no monitor).

## Sources

- Tran & Yu, arXiv:2610.28787 — abstract fetched 24 Oct 2026.
- Lee 2026, SSRN 7426061 — **403; pack claim only**.
- `../../ai-collusion-compare/project-ranking.md` — blind ranking and union table.
- `../../ai-collusion-compare/final-verdict.md` — the correction and final recommendation.
