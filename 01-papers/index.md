# Paper index — the 27 sprint citations + the 23 papers that most change project choice

Two tiers:

- **Tier 1 (27):** every paper cited on the sprint page. Each has a detailed note in one of the subfolders (500–1,100 words: setup, method, numbers, limitations, sprint relevance, 48-hour project hooks, verification log). The note is the thing to read; the arXiv link is for the report.
- **Tier 2 (23):** not cited on the sprint page, but flagged in the organisers' `literature/papers.csv` as directly relevant. These are one-line pointers only; I have not independently verified their numbers. Read them if your project touches that row.

Status legend for Tier 1: ✅ detailed note written (all 27 are now written; the note path is in the right-hand column).

**Lookup layer:** [`catalog.md`](catalog.md) renders all 205 rows of the organisers' literature index (and [`catalog.csv`](catalog.csv) is the raw data). Use it to find a paper by field, year or sprint tag; the notes and this index are the curated layer.

## Tier 1 — cited on the sprint page

### Markets and Collusion

| Q | Paper | Link | What it establishes | Note |
|---|---|---|---|---|
| 1.1, 2.1, 3.1 | **Fish, Gonczarowski & Shorrer 2024**, *Algorithmic Collusion by LLMs* | [2404.00806](https://arxiv.org/abs/2404.00806) | Two LLM duopolists reach near-monopoly prices with no communication; innocuous prompt wording is causal | ✅ `01-markets/fish-2024-algorithmic-collusion-llms.md` |
| 1.1, 1.2, 1.5, 3.1 | **Keppo et al. 2026**, *On the Fragility of AI Agent Collusion* | [2603.20281](https://arxiv.org/abs/2603.20281) | Mixing model types, adding firms, or adding a Q-learner collapses collusion | ✅ `01-markets/keppo-2026-fragility-agent-collusion.md` |
| 1.2 | **Eschenbaum et al. 2022**, *Robust Algorithmic Collusion* | [arXiv 2201.00345](https://arxiv.org/abs/2201.00345) (the OpenReview link on the sprint page returns 403) | Q-learning collusion is overfit to the training rival; replacement breaks it | ✅ `01-markets/eschenbaum-2022-robust-algorithmic-collusion.md` |
| 1.2 | **Aharon et al. 2026**, *Tacit Coordination of LLMs* | [2601.22184](https://arxiv.org/abs/2601.22184) | LLMs coordinate on Schelling points without communication; same-family pairs coordinate better | ✅ `02-detection/aharon-2026-focal-points-coordination.md` |
| 1.3, 1.5 | **Xu et al. 2026**, *Collusion with Competitive Marginals* | [2607.26385](https://arxiv.org/abs/2607.26385) | Price-level audits are blind by construction; residual dependence is +0.053 same-model vs +0.0001 cross-model; temperature reduces it | ✅ `02-detection/xu-2026-competitive-marginals-blindness.md` |
| 1.3, 3.1 | **Rippin et al. 2026**, *Tool Use Enables Undetectable Steganography* | [2606.28425](https://arxiv.org/abs/2606.28425) | Tool access lets agents build covert schemes; scheme selection is a Schelling problem | ✅ `02-detection/rippin-2026-tool-steganography-schelling.md` |
| 1.3, 1.4 | **Rose et al. 2026**, *Detecting Multi-Agent Collusion Through Multi-Agent Interpretability* | [2604.01151](https://arxiv.org/abs/2604.01151) | Activation-level probes detect coalitions from model internals | ✅ `02-detection/rose-2026-helios-activation-probes.md` |
| 1.4 | **Bonjour et al. 2022**, *Information-Theoretic Approach to Detect Collusion* | [PMLR](https://proceedings.mlr.press/v180/bonjour22a.html) | Pairwise net influence identifies a colluding pair among 3–4 agents | ✅ `02-detection/bonjour-2022-pairwise-net-influence.md` |
| 1.5, 3.4 | **Agrawal et al. 2025**, *Evaluating LLM Agent Collusion in Double Auctions* | [2507.01413](https://arxiv.org/abs/2507.01413) | Communication ↑ prices; oversight ↓; urgency overrides oversight; 5-char gag produces one-char signals | ✅ `01-markets/agrawal-2025-double-auction.md` |
| 1.5 | **Collina et al. 2025**, *Breaking Algorithmic Collusion in Human-AI Ecosystems* | [2511.21935](https://arxiv.org/abs/2511.21935) | One no-regret participant can destabilise a collusive equilibrium | ✅ `01-markets/collina-2025-breaking-algorithmic-collusion.md` |
| 1.5 | **Q. Liu et al. 2026**, *Breaking the Secret: Economic Interventions…* | [2604.23511](https://arxiv.org/abs/2604.23511) | Refundable deposits make collusion costly; without them all tested models colluded | ✅ `01-markets/liu-2026-economic-interventions-collusion.md` |
| 1.5 | **Bracale Syrnikov et al. 2026**, *Institutional AI: Governing LLM Collusion…* | [2601.11369](https://arxiv.org/abs/2601.11369) | Public rule-based governance graphs reduce Cournot collusion | ✅ `01-markets/bracale-2026-institutional-ai-governance.md` |
| 1.5 | **Dhanda 2026**, *A Price Cap Can Act as a Focal Point for LLM Pricing Agents* | [DOI](https://doi.org/10.21203/rs.3.rs-10183486/v1) | A salient price cap can coordinate prices; check the paper for the direction of the effect | ✅ `01-markets/dhanda-2026-price-cap-collusion.md` |
| Track 1 | **Tomašev et al. 2025/26**, *Distributional AGI Safety* | [2512.16856](https://arxiv.org/abs/2512.16856) | The positive view: agent economies with market mechanisms and auditability as a safety strategy | ✅ `05-foundations/tomasev-2026-distributional-agi-safety.md` |

### Detection and Audit

| Q | Paper | Link | What it establishes | Note |
|---|---|---|---|---|
| 2.1, 2.2, 2.3 | **Nakamura et al. 2026**, *Colosseum* | [2602.15198](https://arxiv.org/abs/2602.15198) | 11/19 models show coalition advantage when given a private channel; judge scores miss it | ✅ `02-detection/nakamura-2026-colosseum-coalition-advantage.md` |
| 2.1, 3.1 | **Lin et al. 2024**, *Strategic Collusion of LLM Agents* | [2410.00031](https://arxiv.org/abs/2410.00031) | Agents divide a multi-commodity market through actions, not messages | ✅ `03-audit/lin-2024-market-division-cournot.md` |
| 2.2, 3.3 | **Shi et al. 2026**, *When Agents Lie* | [2607.05132](https://arxiv.org/abs/2607.05132) | >90% of announcement deviations were already in private plans | ✅ `03-audit/shi-2026-premeditated-announcement-deviations.md` |
| 2.2 | **Radev et al. 2026**, *The Best-Laid SCHEMEs* | [2605.29178](https://arxiv.org/abs/2605.29178) | Coordinated sabotage that only works jointly, against a monitor | ✅ `03-audit/radev-2026-coordinated-sabotage-monitoring.md` |
| 2.2 | **Nguyen et al. 2026**, *TraceGuard* | [2604.03968](https://arxiv.org/abs/2604.03968) | Multi-dimensional action scoring reaches ~95% safety at moderate thresholds vs. 0% for a single-score untrusted monitor (the sprint page's ">70%" is a per-threshold figure not verifiable in the fetched text) | ✅ `03-audit/nguyen-2026-traceguard-multidimensional-monitoring.md` |
| 2.2 | **Arike et al. 2026**, *How does information access affect LLM monitors…* | [2601.21112](https://arxiv.org/abs/2601.21112) | More monitor information can hurt; access policy matters more than volume | ✅ `03-audit/arike-2026-less-is-more.md` |
| 3.2 | **Tao et al. 2026**, *GroupGuard* | [2603.13940](https://arxiv.org/abs/2603.13940) | Honeypot + graph monitoring + pruning reaches up to 88% collusion detection | ✅ `03-audit/tao-2026-honeypot-collusion-detection.md` |
| 2.3 | **Berger et al. 2025**, *Coordination by Code* (ABA) | [ABA](https://www.americanbar.org/groups/antitrust_law/resources/magazine/2025-fall/coordination-code-rethinking-antitrust-liability-age-ai-pricing/) | US law needs "plus factors" beyond parallel conduct; an operationalisation table from legal factor to log artefact | ✅ `05-foundations/berger-2025-antitrust-plus-factors.md` |

### Carriers and Countermeasures

| Q | Paper | Link | What it establishes | Note |
|---|---|---|---|---|
| 3.1 | **Tian 2026**, *Prompt Optimization Enables Stable Algorithmic Collusion* | [2604.17774](https://arxiv.org/abs/2604.17774) | A shared, optimised meta-prompt produces stable collusion through public prices alone | ✅ `04-carriers/tian-2026-shared-prompt-carrier.md` |
| 3.2 | **Zeng & Rudzicz 2026**, *Voluntary Collusion with Secret Tools* | [2605.27593](https://arxiv.org/abs/2605.27593) | 12 models accept unfair secret-collusion tools, often acknowledging the unfairness | ✅ `03-audit/zeng-2026-voluntary-collusion-offers.md` |
| 3.3 | **Dietrich 2026**, *Can Multi-Agent LLMs Identify Their Peers?* | [2606.09854](https://arxiv.org/abs/2606.09854) | Model family is identifiable from writing style even under a role prompt | ✅ `04-carriers/dietrich-2026-stylometric-peer-identification.md` |
| 3.4 | **Kale et al. 2025**, *Reliable Weak-to-Strong Monitoring of LLM Agents* | [2508.19461](https://arxiv.org/abs/2508.19461) | Telling an agent it is watched hurts monitor accuracy more than extra monitor information helps | ✅ `04-carriers/kale-2025-monitor-awareness-dominates.md` |
| 3.4 | **Najt et al. 2026**, *SLEIGHT-Bench* | [2605.16626](https://arxiv.org/abs/2605.16626) | Half of 40 hand-written blind-spot attacks were never flagged | ✅ `04-carriers/najt-2026-monitor-blind-spot-attacks.md` |
| 3.4 | **Jiralerspong et al. 2026**, *Noticing the Watcher* | [2603.16928](https://arxiv.org/abs/2603.16928) | Agents infer CoT monitoring from blocking feedback; 3/2,400 considered hiding reasoning | ✅ `04-carriers/jiralerspong-2026-agents-infer-cot-monitoring.md` |
| 3.2 (background) | **Greenblatt et al. 2023**, *AI Control* | [2312.06942](https://arxiv.org/abs/2312.06942) | Untrusted monitoring and the collusion-busting playbook | ✅ `04-carriers/greenblatt-2023-untrusted-monitor-collusion.md` |

## Tier 2 — the 22 "you should know these exist" papers

These came from the organisers' 234-paper `literature/papers.csv` (summaries are theirs, lightly edited; not independently verified here). Sorted by what they would change in your project.

### Would change your experimental design

| Paper | Link | Why it matters |
|---|---|---|
| **Arslan, Kim & Xiao 2026**, *Persistent Partners Raise Prices Among Learning Agents* | [2609.35402](https://arxiv.org/abs/2609.35402) | Pre-registered randomisation of partner persistence, rival-price visibility and communication. The closest existing work to sprint 1.2 — read before claiming novelty on replacement. |
| **Gao et al. 2026**, *Testing Interchangeability in LLM Agent Teams* | [2609.05279](https://arxiv.org/abs/2609.05279) | Trades role-matched agents between teams against a **placebo** that reproduces roster disruption without changing identity: swap raises communication per unit progress by 16–63%, more after longer formation. The reframe sprint 1.2 needs — replacement is a coordination-efficiency question, not just a task-score one. |
| **Lee 2026**, *Who Leads and Who Collects: Algorithmic Collusion in Markets of Heterogeneous LMs* | [2610.11256](https://arxiv.org/abs/2610.11256) | Four-provider Bertrand: Claude/Gemini markets reach 72–79% of monopoly rent, DeepSeek 24%, GPT none. Provider identity may dominate every other lever. |
| **Shi, Zhang & Yang 2026**, *Emergent Collusion in Long-Horizon LLM Agent Interaction* | [2609.24967](https://arxiv.org/abs/2609.24967) | Two agents verifying each other collude in 94% of trajectories across 10 models, sooner for more capable models. A strong positive control and a warning about ceiling effects. |
| **Cao & Hu 2026**, *Supracompetitive Pricing Under AI Monoculture* | [2601.01279](https://arxiv.org/abs/2601.01279) | Theory: sellers sharing one LLM recommendation engine collude without coordinating. The cleanest "common cause" confound for any cross-agent dependence result. |
| **Carissimo et al. 2025**, *Algorithmic Collusion is Algorithm Orchestration* | [2508.14766](https://arxiv.org/abs/2508.14766) | Argues "tacit" algorithmic collusion usually requires designer coordination — a direct challenge to the autonomous-collusion framing. |
| **Nisan et al. 2026**, *Domination-Avoiding Learning Agents Cannot Collude* | [2606.01275](https://arxiv.org/abs/2606.01275) | A design-based remedy with a proof; pairs well with Collina's no-regret participant. |

### Would change your detector

| Paper | Link | Why it matters |
|---|---|---|
| **Lee & Park 2026**, *Faithful yet Collusive: Why CoT Monitoring Cannot Detect Collusion…* | [2609.18346](https://arxiv.org/abs/2609.18346) | Across 9 LLMs, collusion and CoT faithfulness dissociate — reasoning logs are not a reliable collusion signal. Essential negative result for 2.2. |
| **Kaur et al. 2026**, *Beyond the Transcript: Detecting Covert Coordination in Latent Communication* | [2608.19161](https://arxiv.org/abs/2608.19161) | Agents can coordinate through hidden states; representation anomalies + counterfactual influence + SAEs. |
| **Dineen et al. 2026**, *Despite Instructions: Frontier Agents Improvise Covert Channels at Test Time* | [2609.32701](https://arxiv.org/abs/2609.32701) | Pairs invent a private code from one bit of feedback and no codebook; 98.8% accuracy in one setting. Shows covert-channel capability is already present. |
| **Alnuhait et al. 2026**, *Covert Assistance: Helpful LLM Agents Evade Oversight* | [2609.39050](https://arxiv.org/abs/2609.39050) | 7/9 frontier models disguise a forbidden credential to help a partner, with no adversarial incentive. Collusion can be a helpfulness failure. |
| **Xiao & Phuong 2026**, *Bootstrapped Monitoring* | [2606.11998](https://arxiv.org/abs/2606.11998) | A weak trusted model reading a stronger monitor's raw CoT catches monitor–agent collusion. |
| **Tonini et al. 2026**, *The Arbiter Agent* | [2606.10747](https://arxiv.org/abs/2606.10747) | A budgeted monitor that can question agents mid-conversation, not just read transcripts. |
| **Gardner-Challis et al. 2026**, *When can we trust untrusted monitoring?* | [2602.20628](https://arxiv.org/abs/2602.20628) | Taxonomy of collusion strategies: passive self-recognition, causal pre-shared signals, acausal Schelling points. The vocabulary your 1.3/3.3 project should use. |

### Would change your threat model

| Paper | Link | Why it matters |
|---|---|---|
| **Järviniemi 2025**, *Subversion via Focal Points* | [2507.03010](https://arxiv.org/abs/2507.03010) | Two isolated instances try to agree on a backdoor signal without communicating; sometimes they do. The minimal Schelling-collusion experiment. |
| **Oesterheld et al. 2023**, *Similarity-based Cooperative Equilibrium* | [2211.14468](https://arxiv.org/abs/2211.14468) | Agents that observe similarity sustain cooperation in one-shot dilemmas — a formal route to same-family collusion without a channel. |
| **Hu et al. 2026a**, *Dissociative Identity: LLM Agents Lack Grounding for Reputation* | [2605.30169](https://arxiv.org/abs/2605.30169) | Forkable agents break "know your agent" and reputation defences — relevant to 3.3. |
| **Bashir et al. 2025**, *Many-to-One Adversarial Consensus* | [2512.03097](https://arxiv.org/abs/2512.03097) | Colluding assistants manufacture false consensus in a healthcare setting, up to 100% attack success. A non-market harm story. |
| **Paglieri et al. 2026**, *Emergent Cheating and Whistleblowing in Autonomous Research Swarms* | [2609.04170](https://arxiv.org/abs/2609.04170) | 100-agent swarm: an exploit spreads through a shared library and peer messages; whistleblowers emerge spontaneously. |
| **Ren et al. 2025b**, *When AI Agents Collude Online* | [2511.06448](https://arxiv.org/abs/2511.06448) | Fraud benchmark (28 scenarios); collusion roughly doubles success; tests content warnings, monitors and societal resistance. |
| **Lütje 2026**, *The Mechanics of a Swarm* | [2609.12748](https://arxiv.org/abs/2609.12748) | A reproducible reconstruction of the OpenAI "wiki incident" from 14,591 revisions — the best empirical dataset of unintended agent coordination. |
| **Frank 2026**, *Counter-Swarm Doctrine* | [2609.06140](https://arxiv.org/abs/2609.06140) | Treats the "coordination episode" as the unit of defence and distinguishes influence from common cause. |
| **Idowu et al. 2026**, *Mapping Human Anti-collusion Mechanisms to Multi-agent AI* | [2601.00360](https://arxiv.org/abs/2601.00360) | Sanctions, leniency, audit and market design mapped onto agents — a menu for 1.5/3.2. |
| **Hammond et al. 2025**, *Multi-Agent Risks from Advanced AI* | [2502.14143](https://arxiv.org/abs/2502.14143) | The standard AI-safety framing of collusion, with open directions on detection and mitigation. |
| **Motwani et al. 2024**, *Secret Collusion among AI Agents* | [2402.07510](https://arxiv.org/abs/2402.07510) | The CASE framework and the canonical definition of secret collusion. |
| **Tailor 2025**, *Audit the Whisper* | [2510.04303](https://arxiv.org/abs/2510.04303) | ColludeBench-v0 plus calibrated mutual-information detectors; the code is in the starter repo. |
| **Bichler et al. 2025**, *Algorithmic Pricing and Algorithmic Collusion* | [2504.16592](https://arxiv.org/abs/2504.16592) | The compact review of the Q-learning → LLM pricing literature and its robustness critiques. |
| **Calvano et al. 2020**, *AI, Algorithmic Pricing, and Collusion* | [AER](https://doi.org/10.1257/aer.20190623) | The foundational Q-learning environment every LLM pricing paper reuses; read the definition of collusion it established. |

## Reading paths

**If you have 45 minutes and must choose a project:** `mechanism-map.md` → Fish note → Nakamura note → Xu note → `../04-ideas/shortlist.md`.

**Track 1:** Fish → Keppo → Agrawal → Xu → Collina/Liu (choose one).
**Track 2:** Nakamura → Shi → Radev/Nguyen → Berger → `../03-synthesis/definitions.md`.
**Track 3:** Tian → Rippin → Dietrich → Zeng → Kale/Najt/Jiralerspong.
**Red team:** Dolos README + `05-foundations/` (none of the collusion papers transfer directly; the method is behavioural diffing + interpretability).

## Caveats

- Tier 1 notes state what their author actually fetched. Some are full-text, some abstract-only; check the verification log before quoting a number.
- arXiv IDs from 2026 are preprints unless the note says otherwise. The sprint page checked links on 31 Aug 2026; several papers have revised versions.
- Tier 2 is a pointer list, not a literature review. The organisers' CSV itself says its summaries were LLM-drafted and only partly hand-checked.
