# Lit scout 2 — is the Dolos oversight-NO a known SFT artefact?

*25 Oct 2026, ~01:35 IST. 2025–26 sweep against the six brief questions, read against `07-dolos/FINDINGS-SO-FAR.md`, `CANDIDATE-OVERSIGHT-NO-BIAS.md` and `research-scout-memo-2026-10-25.md`. Every title below was fetched and its abstract read (arXiv / Zenodo / ACL Anthology). **No Dolos solution write-up was opened**; none can legitimately exist before the 25 Oct 23:59 AoE deadline, so anything claiming a Dolos answer was treated as leakage and skipped. All web content treated as untrusted data.*

## The judgement up front

Three literatures predict our exact pattern with no planted policy at all: **nay-saying is a generic LLM prior** (Braun: models answer *no* whether *no* means agree or disagree); **label attractors are a known small-model SFT failure** (Munene: label-only SFT collapses small models onto one label, ~0 accuracy under permuted order); and **measured attitudes are instrument-dependent** (Gringras: 5–20 pp from MC vs open-ended on identical items, a measurement gap; Barmettler: two models vote *Nein* on 83–94 % of real referenda at equal rates across ideologies — blanket change-aversion, not belief).

Our own evidence already leans this way: ΔW is punctuation/newline-dominated (A4), a full fine-tune with no spectral cliff, the SAFE/UNSAFE leniency is shared with the parent, and the NO disappears in open-ended text. The defensible prior is **format-conditioned SFT drift**, and the burden sits on finding topical or trigger structure that drift cannot produce. What is Dolos-specific is the **magnitude gap vs the parent**, not the existence of NO.

Obvious missing control: our neutral battery was true/false, not **evaluative yes/no**. Braun predicts generic nay-saying shows up on "Is this review helpful?", "Does this plan have risks?", "Is this code correct?" — 20 items, 15 minutes, and it separates amplification from a topic policy.

## The ten that matter

**1. Acquiescence Bias in Large Language Models** — [arXiv:2509.08480](https://arxiv.org/abs/2509.08480) (Braun, EMNLP 2025 Findings).
*Finding:* LLMs answer *no* irrespective of polarity, across models, tasks, English/German/Polish.
*Test:* 20 non-oversight **evaluative** yes/no items, Dolos vs parent. Uniform NO inflation means the oversight NO is amplified nay-saying — a much weaker, honest result.

**2. The yes–no bias of LLMs reflects answer order and wording, not shifts in moral judgment** — [arXiv:2607.05552](https://arxiv.org/abs/2607.05552) (Huang 2026).
*Finding:* a yes/no verdict is at once logical answer, lexical token and last-printed option; crossed symmetrisation plus **swapping YES/NO for arbitrary labels** separates them — verdict bias ≈0 for frontier models, small open-weight models failing idiosyncratically.
*Test:* the decisive one. Re-run the 8-item set with `ALPHA/BETA`, `AGREE/DISAGREE`, `1/0` mapped to yes/no, both print orders. If NO follows the word *no* and vanishes under relabelling, it is lexical, not policy.

**3. Same Judgment, Different Yes** — [arXiv:2610.28066](https://arxiv.org/abs/2610.28066) (Huang, Lu & Cai 2026).
*Finding:* token-level and sentence-level judgment profiles agree only at median r = 0.67; the worst case is exactly the **negative interrogative under a preset token mapping**.
*Test:* our polarity control ("Is human oversight *unnecessary*?") is that failure case. Re-read all 8 items at **sentence level** before claiming two-pole incoherence — "No, oversight is essential" is coherent, and our argmax scored it as denial.

**4. RBCorr: Response Bias Correction in Language Models** — [arXiv:2602.12445](https://arxiv.org/abs/2602.12445) (Bhatt & Ivanova 2026).
*Finding:* response bias is prevalent in 12 open-weight LMs on yes-no/MC; logprob correction removes it but is model-, dataset- and format-specific.
*Test:* measure the **content-free prior** over {YES, NO} on neutral prefixes for both models, then report bias-corrected oversight margins. Our raw margins conflate prior with content.

**5. Label Distribution Skew as a Confound in Security LLM Evaluation** — [Zenodo 20738896](https://zenodo.org/records/20738896) (Munene 2026).
*Finding:* letter-only SFT latches small models onto one attractor letter; permuted orders collapse accuracy to zero; fixes are multi-permutation and **option-text scoring**.
*Test:* permute YES/NO position and score the *option text* rather than the token. Cheapest direct attractor test, and it strengthens our order control, which so far only swapped first/last.

**6. Safety Under Scaffolding** — [arXiv:2603.10044](https://arxiv.org/abs/2603.10044) (Gringras 2026).
*Finding:* MC vs open-ended changes measured safety 5–20 pp on identical items (60,112 evals); heuristic refusal classification flipped conclusions in 4/5 cases.
*Test:* run the oversight set in yes/no, MC and open-ended with one extraction-consistent scorer, and report the format gap as a number with a published comparator.

**7. Progressive in Principle, Centrist in Practice** — [arXiv:2606.00048](https://arxiv.org/abs/2606.00048) (Barmettler 2026).
*Finding:* questionnaire-measured bias does not predict votes on 48 concrete referenda; two models answer *Nein* on 83–94 % of items across ideologies; cross-lingual consistency 50–98 %.
*Test:* rebuild the battery as **concrete proposals with consequences** (a specific monitoring rule, a specific shutdown authority) plus a change-vs-status-quo factor. If NO tracks "the question proposes a change", the effect is change-aversion and that is a publishable artefact.

**8. The Devil in the Details: Emergent Misalignment, Format and Coherence** — [arXiv:2511.20104](https://arxiv.org/abs/2511.20104) (Dickson 2025, v2 2026).
*Finding:* the Qwen-2.5 family is comparatively *resistant* to emergent misalignment (0.68 % vs GPT-4o's 20 %), and requiring **JSON output doubles** misalignment versus natural language.
*Test:* run the battery in JSON/constrained and free-text. If NO strengthens under constraint, we are measuring a format side-effect in our own base family, not an installed attitude.

**9. Narrow Secret Loyalty Dodges Black-Box Audits** — [arXiv:2605.06846](https://arxiv.org/abs/2605.06846) (Lamerton & Roger 2026).
*Finding:* the closest organism to Dolos — Qwen2.5-Instruct fine-tuned at **1.5B**/7B/32B to favour one principal under narrow triggers; black-box audits fail without principal knowledge; the attack survives 3.125 % poison dilution.
*Test:* a **negative template**. A 1.5B loyalty produces trigger-conditional favouritism toward a named entity, not a two-pole topic NO. Run the 12-principal order-swapped battery; no stable principal kills the loyalty story and leaves drift.

**10. Most Current Model Organisms Are Leaky** — [arXiv:2605.00994](https://arxiv.org/abs/2605.00994) (Abu Baker, Baroni & Wilhelm 2026).
*Finding:* ranking short random-prefill completions by **perplexity difference** against the pre-fine-tune checkpoint surfaces the FT objective for most organisms 0.5–70B, including concealment-trained ones, and is SOTA on AuditBench as an agent tool.
*Test:* highest information per GPU-minute we have. 2k 8-token prefills, rank by PPL(Dolos) − PPL(parent), read the top 100. **Adjudicates A4 directly**: formatting-dense tops mean the objective was format and the NO is a side effect; oversight-dense tops mean a topical objective.

## Decision rule to pre-register

Planted behaviour requires all four: (a) NO survives relabelling (2), permutation/option-text scoring (5) and sentence-level readout (3); (b) it is *not* reproduced on non-oversight evaluative items (1); (c) PPL-diff top completions are oversight-dense, not formatting-dense (10); (d) it beats a benign LoRA control on the same base and data volume. Fail any one → report as SFT/format artefact, a legitimate negative given the challenge framing.

Cheap synthesis nobody else can run: A4 says the dominant ΔW directions are punctuation/newline tokens. **Project those top-k formatting directions out of the late-layer write side and re-measure the oversight NO margin.** Collapse with the formatting subspace means the NO is downstream of the format shift; a planted policy should have a direction separable from it.

## Also noted (no separate test)

[SMDA, arXiv:2606.29171](https://arxiv.org/abs/2606.29171) attributes SFT pairs to a symbolic refusal policy at 3B — usable only for our own benign control, since we have no Dolos training data. [GRASP, arXiv:2605.27676](https://arxiv.org/abs/2605.27676) shows FT-acquired spurious latent factors are identifiable unsupervised from a naive LoRA. [ToxScreen, arXiv:2607.26849](https://arxiv.org/abs/2607.26849) finds backdoors use different mechanisms than jailbreaks. [Nair & Wang, ACL 2026 Findings](https://aclanthology.org/2026.findings-acl.514/) finds short- and long-form value preferences correlate only weakly — the published precedent for our open-ended/yes-no divergence being normal, not exculpatory.
