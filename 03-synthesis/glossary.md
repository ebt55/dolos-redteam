# Glossary

Terms you will meet in the notes and the sprint brief. Definitions are working definitions for this folder, not canonical ones.

## Collusion concepts

**Algorithmic collusion** — supracompetitive outcomes produced by algorithms without explicit human design to collude. The economics literature usually does **not** require communication, intent or agreement.

**Tacit collusion** — coordination without an explicit agreement, sustained by repeated interaction and the threat of retaliation. In pricing games, the test is usually price elevation plus a punishment response.

**Explicit collusion** — an actual agreement, often with communication. The legal cartel case. In LLM experiments, usually induced by a prompt (the "smoking gun" condition).

**Autonomous collusion** — collusion that emerges from learning or in-context adaptation without any instruction to collude. Fish et al. is the canonical LLM demonstration.

**Collusion index (Δ)** — a normalised price or profit measure: 0 at the competitive (Nash) benchmark, 1 at the joint-monopoly benchmark; negative values indicate a price war below competition. Used by Calvano, Dhanda, Keppo and others. Always check which benchmark and which window (e.g. last 10 rounds) a paper uses.

**Coalition advantage (Δ-collusion)** — Colosseum's metric: the gap between the non-coalition agents' mean regret and the coalition's mean regret, normalised so 0.5 is a tie and >0.5 favours the coalition. Requires a computable nominal objective and, in practice, a known coalition.

**Reward–punishment / grim trigger** — a strategy that charges a high price and retaliates after a deviation, then forgives slowly. The standard mechanism behind tacit collusion; detected by regressing an agent's price on rivals' recent prices.

**Parallel conduct** — firms behaving similarly without evidence of agreement. In US antitrust, parallel conduct alone is **not** illegal.

**Plus factors** — additional evidence courts use to infer an agreement from parallel conduct: prior collusion, intent to coordinate, market structure, and whether the information shared is current, specific, bilateral and competitively sensitive.

**Hub-and-spoke** — a coordination structure in which a common vendor or platform (the hub) links competitors (the spokes), e.g. RealPage, Cendyn, ATPCO.

**Concerted practice** — the EU-law analogue of an agreement (Art. 101 TFEU); can be inferred from awareness plus conformity, as in *Eturas*.

**Secret collusion** — coordination hidden from an overseer, usually via steganography or a covert channel. The AI-safety notion; requires concealment.

**Common cause** — correlated behaviour produced by a shared origin (same model, same vendor, same training data) rather than by interaction. The main confound for dependence-based detectors; Xu's cross-model baseline (+0.0001) is the cleanest control.

## Games and environments

**Bertrand competition** — firms compete on price; with homogeneous goods and no capacity constraints, the static Nash price equals marginal cost. The workhorse of the LLM pricing literature.

**Cournot competition** — firms compete on quantity; price clears the market. Used by Lin et al. and Bracale et al.

**Logit demand** — a demand system where each firm's share depends on its price relative to rivals' prices and an outside option. Calvano et al.'s parameterisation is reused by Fish, Keppo, Dhanda and others.

**Continuous double auction (CDA)** — buyers and sellers post bids and asks continuously; trades occur when they cross. Agrawal et al.'s environment.

**DCOP** — distributed constraint optimisation problem: agents choose a joint assignment to maximise a decomposable objective. Colosseum's formalism.

**Nash equilibrium** — a profile where no agent can gain by unilaterally changing its action. The competitive benchmark in most pricing experiments.

**Monopoly / joint-profit benchmark** — the price or profit a single firm controlling all sellers would choose. The upper bound of the collusion index.

**Schelling point / focal point** — a salient solution people (or models) converge on without communicating, e.g. "meet at Grand Central at noon". Relevant to coordination without a channel and to covert signalling.

**Coordination index (NCI)** — Aharon et al.'s measure of how often independently sampled answers agree, compared with human focal-point data.

## Methods and statistics

**Condition / arm** — one level of the manipulated variable. "Chat on" and "chat off" are two arms.

**Seed** — the random seed for a run. Report the number of seeds, not the number of rounds, as your N for a collusion experiment: rounds within a run are not independent.

**Positive control** — a condition where the effect is known to exist, used to prove the harness can detect it. E.g. reproduce Fish-style supracompetitive pricing before testing a new lever.

**Benign / negative control** — a condition where the effect should be absent, used to estimate false positives. E.g. same-model agents with no channel, or the Gibson-like shared-advisor condition.

**Pre-registration** — fixing the hypothesis, metric and threshold before seeing test data. In a weekend, write it in the report skeleton and commit it.

**FPR / TPR / AUC** — false-positive rate, true-positive rate, area under the ROC curve. A detector report without an FPR is not interpretable.

**Permutation test** — a null distribution built by shuffling labels; used by Xu for the temperature effect and by Bonjour-style dependence tests.

**Bootstrap CI** — resampling-based confidence interval. Resample **seeds**, not rounds.

**Effect size** — the magnitude of the difference, ideally with a CI. "Significant" is not "large".

**Power** — the probability of detecting an effect if it exists. A null result with low power is uninformative.

**LLM judge** — a model scoring transcripts on a rubric. Cheap and useful, but it measures talk; it can anti-correlate with action-level metrics.

**Chain of thought (CoT)** — the model's visible reasoning. Useful for diagnosis, unreliable as a collusion detector (Lee & Park; Shi).

**Activation probe** — a classifier trained on internal model activations to detect a concept or coalition. Requires white-box access.

**Sparse autoencoder (SAE)** — a dictionary-learning method for interpreting activations. Mentioned in latent-channel detection work.

**Stylometry** — identifying the author (or model family) of a text from style features. Dietrich's T5 classifier reaches F1 ≈ 0.99.

**HHI** — Herfindahl–Hirschman index, a concentration measure. Xu uses it to show that counting distinct operators changes the picture (+247.5%).

## Sprint and infrastructure

**AoE (Anywhere on Earth)** — UTC−12. The sprint deadline is 25 Oct 23:59 AoE = 26 Oct 17:29 IST.

**Model organism** — a model deliberately trained to exhibit a behaviour for study. Dolos-1.5B is one.

**Red team** — an adversarial audit trying to discover a model's hidden behaviour or bypass its safeguards.

**Untrusted monitoring** — a control protocol in which a less-trusted model monitors another model. The core failure mode is monitor–policy collusion.

**AI control** — the field that designs protocols to prevent a capable but untrusted model from causing harm, usually assuming it is actively trying to subvert the protocol.

**Stigmergy** — coordination through modifications to a shared environment (a wiki, a cache, a file store) rather than direct messages. The OpenAI wiki and Artifactory incidents are stigmergic.

**Terrarium / CoLLAB** — the agent runtime and cooperative-task benchmark that Colosseum builds on.

**Branching / checkpoint** — saving a run's history and continuing it with a changed participant or condition. `branch_game.py` in the starter repo.

**Harness** — the code that turns a model into an agent: prompts, tools, memory, parsing, loop. A confound in cross-paper comparisons.

**Prompt prefix** — the opening instruction text varied in Fish-style experiments; a causal lever, not a detail.
