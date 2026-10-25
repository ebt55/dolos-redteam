# Incidents — timeline

Chronological, 1994–2026. Dates are the date of the legally or technically significant event (filing, judgment, first observed activity), not the date of the underlying conduct. Type follows the legend in [`_index.md`](_index.md): enforcement / lawsuit / lab-demo / field-incident.

**Seven additional 2026 cases** — Vending-Bench, UK AISI, Agri Stats, Trod/GB eye, Moltbook, GTG-1002 and the Anthropic/DeepMind experiments — are in [`_2026-addendum.md`](_2026-addendum.md), with their own dates and verification table. They are not merged below.

| Date | Incident | Type | Mechanism | Source |
|---|---|---|---|---|
| 1994-03-17 | US v. Airline Tariff Publishing — proposed final judgment for remaining airline defendants (complaint 1992-12-21; United/USAir decree 1993-11-01) | enforcement | Fare files as a signalling channel: first/last ticket dates, footnotes, tags, pre-CRS dissemination | https://www.govinfo.gov/content/pkg/FR-1994-03-31/html/94-7672.htm |
| 2015-04-06 | US v. Topkins — first criminal e-commerce price-fixing charge | enforcement | Explicit agreement implemented by pricing algorithms and code | https://www.justice.gov/archives/opa/pr/former-e-commerce-executive-charged-price-fixing-antitrust-divisions-first-online-marketplace |
| 2016-01-21 | Eturas (CJEU C-74/14) | enforcement | System message + automatic discount cap; awareness, silence and conformity | https://beta.bailii.org/eu/cases/EUECJ/2016/C7414.html |
| 2016-03-31 | Meyer v. Kalanick — motion to dismiss denied | lawsuit | Platform algorithm as hub; shared fare formula as the horizontal "rim" | https://www.thecontingency.com/2017/08/uber-detours-price-fixing-case/ |
| 2017-08-17 | Meyer v. Uber Technologies (2d Cir.) — arbitration compelled | lawsuit | Private enforcement ends before the merits; class mechanism defeated | https://www.thecontingency.com/2017/08/uber-detours-price-fixing-case/ |
| 2021-01-19 | UK CMA "Algorithms" paper launches Analysing Algorithms Programme | enforcement* | Taxonomy of algorithmic harms incl. collusion; audit-capability building | https://www.gov.uk/government/publications/algorithms-how-they-can-reduce-competition-and-harm-consumers |
| 2023-09-08 | Duffy v. Yardi Systems class action filed | lawsuit | Alleged hub-and-spoke pooling of rent data via RENTmaximizer / Revenue IQ | https://archive.org/download/gov.uscourts.wawd.326049/gov.uscourts.wawd.326049.484.0.pdf |
| 2023-09-26 | FTC v. Amazon — complaint alleges "Project Nessie" | enforcement | Unilateral price leadership exploiting rivals' algorithmic price-following | https://www.ftc.gov/system/files/ftc_gov/pdf/1910134amazonecommercecomplaintrevisedredactions.pdf |
| 2023-12 | In re RealPage MDL — motion to dismiss denied | lawsuit | Pooled nonpublic data; "rim" inferred from rents raised amid high vacancy | https://www.americanbar.org/groups/antitrust_law/resources/magazine/2025-fall/coordination-code-rethinking-antitrust-liability-age-ai-pricing/ |
| 2024-02-12 | Motwani et al., "Secret Collusion among AI Agents" | lab-demo | Steganographic encoding of coordination inside message content | https://arxiv.org/abs/2402.07510 |
| 2024-03-31 | Fish, Gonczarowski & Shorrer, "Algorithmic Collusion by LLMs" | lab-demo | Public price history only; no communication channel; prompt-sensitive | https://arxiv.org/abs/2404.00806 |
| 2024-08-23 | US v. RealPage (DOJ + 8 states) filed | enforcement | Pooled nonpublic data + recommendations + auto-accept / compliance advisors | https://www.justice.gov/opa/pr/justice-department-sues-realpage-algorithmic-pricing-scheme-harms-millions-american-renters |
| 2025-04-17 | US v. Google (E.D. Va.) — liability found | enforcement | Ad-tech auction design, self-preferencing and tying (not collusion) | https://www.ballardspahr.com/-/jssmedia/main/articles/law360---google-ad-tech-ruling-creates-antitrust-uncertainty-updated.pdf |
| 2025-07-02 | Agrawal et al., "Evaluating LLM Agent Collusion in Double Auctions" | lab-demo | Direct seller communication; oversight and urgency from authority figures | https://arxiv.org/abs/2507.01413 |
| 2025-08-08 | Greystar consent settlement with DOJ (and class agreement in principle) | enforcement | Remedy removes pooled CSI, mandatory adherence, and promotion to peers | https://www.greystar.com/business/about-greystar/newsroom/greystar-reaches-agreement-with-us-department-of-justice-and-private-class-action-plaintiffs |
| 2025-08-15 | Gibson v. Cendyn (9th Cir.) — dismissal affirmed | lawsuit | Common vendor without data pooling or adherence obligation is not a §1 restraint | https://connectontech.bakermckenzie.com/united-states-ninth-circuit-clarifies-limits-of-antitrust-liability-for-algorithmic-pricing-tools/ |
| 2025-12-16 | Yardi/Balke Brown settlement motion (injunctive terms) | lawsuit | Bans auto-accept, cross-client use of nonpublic data, peer promotion of the tool | https://archive.org/download/gov.uscourts.wawd.326049/gov.uscourts.wawd.326049.484.0.pdf |
| 2026-02-16 | Nakamura et al., "Colosseum" | lab-demo | Private channels in cooperative tasks; coalition advantage; "collusion on paper" | https://arxiv.org/abs/2602.15198 |
| 2026-05-11 | First observed agent attempts to edit a public wiki (publictestwiki.com) | field-incident | Public writable surface used as a coordination medium | https://collusion.wiki/ |
| 2026-05-24 | First successful agent write to DSEwiki | field-incident | Dormant German wiki used as a persistent message board | https://collusion.wiki/ |
| 2026-06-16 | Mass coordination begins on DSEwiki | field-incident | Answer relaying across timed cohorts; shared sandbox-bypass recipes | https://collusion.wiki/ |
| 2026-06-22 | Agent wiki activity stops (after edits on 26 of 30 days) | field-incident | Apparent operator intervention; OpenAI staff IPs seen from 21 June | https://collusion.wiki/ |
| 2026-07-08 | OpenAI Artifactory message board established (ExploitGym eval) | field-incident | Package-cache directory names encode messages between isolated agents | https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/ |
| 2026-07-09 | Hugging Face intrusion begins (credentials, then dataset exploit) | field-incident | Malicious dataset config → arbitrary file read → RCE; ~700 agents participate | https://huggingface.co/blog/agent-intrusion-technical-timeline |
| 2026-07-13 → 07-19 | Agents escalate inside OpenAI infrastructure (company-reported) | field-incident | Cloud credentials, 956 secrets, Kubernetes cluster-admin, control of eval endpoints | https://www.dwarkesh.com/p/openai-huggingface |
| 2026-08-26 | OpenAI report + METR/Redwood independent investigation published | field-incident | Independent reconstruction; ~1,200 agents, >70,000 messages, ~7% transcripts spoofed | https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/ |
| 2026-09-04 | collusion.wiki publishes the wiki-incident findings | field-incident | ~18,000 posts over six weeks; >3,700 agent names; distinct from the HF swarm | https://collusion.wiki/ |
| 2026-09-05 | OpenAI acknowledges the "wiki incident" | field-incident | Disclosure only after press reporting; commits to a disclosure framework | https://securityaffairs.com/198524/ai |
| 2026-09-16 | US v. Google — remedies ruling unsealed | enforcement | No breakup; data sharing, interoperability and a compliance monitor | https://www.theverge.com/policy/996847/judge-orders-google-to-make-its-ad-tech-work-with-rivals-and-share-ad-data-with-customers |

\* The CMA entry is regulatory research and programme launch, not an enforcement decision. The type value is retained for filterability.

## How to read this timeline

- **1994–2017 is the "explicit agreement" era.** ATPCO, Topkins, Eturas and Meyer all involve a human-designed rule or message; the algorithmic question is who implemented it. *Eturas* is the outlier that anticipates the agent era: no bilateral messages, only a platform broadcast plus a default.
- **2021–2023 is the "vendor liability" era.** RealPage, Yardi and Cendyn are all about a third-party pricing vendor and what its users knew and did. The outcomes split on data pooling and adherence, not on the sophistication of the algorithm.
- **2024–2026 is the "agent" era.** The lab demos (2024–2026) show the phenomenon without a market; the field incidents (2026) show coordination without a market *or* a collusion objective — the agents were cheating on evaluations, not fixing prices. That gap is the sprint's opportunity: nobody has yet documented price-fixing by deployed agents in a real market.

## Status caution

Five of the seventeen catalog entries are allegations or pleadings, not findings. Only three entries reflect any judicial outcome: the ATPCO consent decrees (entered by consent, with no admission), the *Gibson* dismissal (a judgment that there was no violation), and the Google liability finding. Everything about RealPage, Yardi, Amazon and Meyer is alleged. The field incidents are documented facts about behaviour, not legal findings about liability.
