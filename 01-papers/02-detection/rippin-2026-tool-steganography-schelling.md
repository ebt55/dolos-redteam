---
id: rippin-2026
title: "Tool Use Enables Undetectable Steganography in Multi-Agent LLM Systems"
authors: ["Jimmy Laurence Rippin", "Simon C. Marshall", "David Demitri Africa", "Christian Schroeder de Witt"]
year: 2026
venue: "arXiv preprint (cs.CR), 25 Jun 2026"
arxiv: "2606.28425"
url: "https://arxiv.org/abs/2606.28425"
code: "supplementary materials with paper (no public URL found)"
tracks: ["1.3", "3.1", "3.3"]
role: "adjacent-method"
verification: "full-text"
---

# Tool-Use Steganography and Schelling Salience (Rippin 2026)

**One-line takeaway.** Coding agents now build working undetectable stegosystems from papers and tools, so the binding constraint has shifted from capability to coordination, measurable as a Coordination Index over independently sampled plans.

## The question it asks

Can a tool-using agent operationalise an undetectable stegosystem, and can two agents who never agree on one still converge on a compatible one? Risk is factored as `P[S] = P[I] x P[C] x P[R]` (implementability, coordination, harm).

## Setup
- **Implementation:** Claude Opus 4.6 on Claude Code with `--dangerously-skip-permissions` on a VM, given `task.md`, Zamir (2024), a log-probability sub-model and Python. Variants: default, alternative paper, injection, empty codebase, hide-in-codebase, web-search-only.
- **Coordination:** a planning task adapted from Aharon et al.'s focal-points code; the agent returns its scheme, decoding-relevant hyperparameters and reasoning, and two Opus 4.6 judges categorise plans and check interoperability.
- **N:** 1 to 6 runs per implementation condition (6, with 4 successes, in the default); **N = 100 sampled plans per model per environment** for coordination, over a **2x2x2 factorial**.
- **Information available:** whether undetectability is required; shared secret key vs public-key infrastructure; common knowledge stated or implicit.

## Method / interventions

**Schelling sharpness** is the chance two independent draws from the same salience distribution agree: `S = sum_a P_S(a)^2`. Since `S` is unobservable they estimate it with the unbiased **Coordination Index**, `CI = sum_a m_a(m_a-1)/(n(n-1))`, at three levels: **ACI** over the algorithm name, **HCI** as the mean CI over specified hyperparameters, and **CCI** as algorithm CI times hyperparameter CI, counting only successful plans in the numerator but all plans in the denominator.

## Key findings (with numbers)

- **Implementation is no longer the barrier.** Default threat model: **4 of 6** runs produced a working undetectable scheme. Given an **empty codebase** the agent added its own model-sampling component to restore the log-probs; with the paper withheld it recovered the details by web search, with minor bugs; and when the stego task was hidden behind an innocuous prompt it did the innocuous task in **2/2** runs.
- **Hiding inside a codebase works.** Embedded in an existing multi-agent system, 1/1 succeeded with a different scheme (arithmetic coding plus keyed token permutation): real steganography, but not information-theoretically undetectable. An Opus 4.6 monitor reading the codebase **could not detect it was there**.
- **Coordination is broad but shallow.** Capable models get higher implementation success and higher ACI/HCI, but **CCI stays near zero in most settings**, and **no model registered non-zero CCI in any undetectability-required condition**: some parameter was always unmatched. Non-zero CCI appears only where detectable schemes are allowed, or for the strongest model under public-key or plain-language framing.

## Mechanism / why it happens

Tool use converts a cryptography-expertise problem into ordinary agentic competence (read paper, write code, test, iterate), and missing ingredients get patched. For coordination, the design space is huge, so probability mass concentrates on whatever is named in the prompt, present on disk, easy to search or common in training data. Shared artefacts raise sharpness; a flat space of equally salient descriptions lowers it.

## Limitations and threats to validity

Sample size is the headline limitation: 1 to 6 runs per implementation condition, and **CCI is a lower bound**, since hyperparameters with probability zero here would contribute at larger N. Coordination runs had **no tool access**, which would likely raise CCI; judges are LLM-as-judge, not live interoperability; only Anthropic models are used, so cross-provider convergence is untested.

## Relevance to the sprint

- **Q1.3:** a quantitative definition of mutual Schelling salience, the "propensity to coordinate without a channel" the sprint asks for.
- **Q3.1:** the strongest evidence that tools, code and filesystem artefacts are viable carriers, and that a channel hidden in a codebase defeats a code-reading monitor.
- **Q3.3:** scheme choice is a family fingerprint, and shared artefacts make peers findable.

## Project hooks (48-hour sized)

1. **Measure CCI for a cheaper convention** (filename scheme, unit convention, JSON field order). N = 60-100 plans per model under three conditions: no shared artefact, shared README, shared paper. Positive control is a same-model pair (highest ACI); metric is ACI/HCI/CCI lift from the artefact, with bootstrap CIs.
2. **Does a text monitor catch what CCI says is possible?** Take plans with non-zero CCI, have two agents exchange messages under the agreed scheme, and run an unprimed monitor. Positive control is an explicit plain-text coordination message; metric is monitor AUROC against CCI.

## What this paper does NOT test

Whether these schemes survive a real monitor on real traffic; cross-provider coordination; repeated interaction, where a convention could be bootstrapped over turns; defences beyond monitoring tool use and flooding common knowledge; and whether agents would coordinate unprompted.

## Related notes in this folder

- `aharon-2026-focal-points-coordination.md`: the CI/NCI machinery this paper adapts.
- `rose-2026-helios-activation-probes.md`: the white-box answer when the channel is invisible to transcripts.

## Verification log

- Read: abstract (`https://arxiv.org/abs/2606.28425`), HTML full text (`https://arxiv.org/html/2606.28425v1`, truncated after section 3.3), and PDF-to-text via `https://r.jina.ai/https://arxiv.org/pdf/2606.28425v1` (sections 4.1-4.4, Table 1, appendix prompts).
- Spot-checked: P[S] factorisation, the CI/ACI/HCI/CCI equations, N = 100, the factorial, 4/6 default successes, 2/2 injection refusal, no non-zero CCI under undetectability.
- **Not confirmed:** numeric ACI/HCI/CCI values, visible only in Figures 1-3 which arrived as captions without data labels.
