# Report template — fill this in as you go, not at the end

A 5–8 page structure that matches what the sprint asks for. Copy it into your repo as `report.md` at hour 1 and fill the sections as results arrive. Export to PDF before submitting.

---

# [Title: say what you found, not what you did]

**Team:** [names] · **Track:** [1 / 2 / 3] · **Sprint question:** [e.g. 1.2] · **Date:** [26 Oct 2026]

## Abstract (150–200 words)

Template:

> We test whether [mechanism] causes [outcome] in [environment]. Prior work shows [known result] ([citation]), but [gap]. We run [N] [conditions] with [models], [seeds] seeds and [rounds] rounds, holding [controls] fixed. [Positive control] reproduces [known result]. We find that [manipulation] [increases/decreases] [metric] by [effect size] (95% CI [..]), while [secondary metric] [does/does not] move. [One-sentence interpretation]. We release [code/logs].

The abstract must contain the headline number. If it does not, the paper has no headline yet.

## 1. Question and claim (0.5 page)

- The question, in one sentence.
- The claim, in one sentence (falsifiable).
- The definition of collusion you are using, with a citation. Say which of the three standards you adopt: outcome elevation, agreement/plus factors, or concealment from an overseer. See `03-synthesis/definitions.md`.
- What would count as evidence *against* your claim.

## 2. Why it matters (0.5 page)

- The sprint question, quoted.
- The real-world stake: one paragraph, one citation (RealPage, Gibson, the OpenAI incident, or the market-harm literature).
- The gap: "X is known in setting A; it is untested in setting B because C."

## 3. Related work (0.75 page)

Five to eight citations, positioned as a gap, not a list:

- What is known about the mechanism (2–3 papers).
- What is known about the environment (1–2).
- What is known about the metric/detector (1–2).
- What is *not* known, and therefore what you do.

## 4. Setup (1.5 pages)

| Item | Value |
|---|---|
| Environment | [game/task, parameters] |
| Agents | [models, provider, version, temperature] |
| N agents | [sellers/buyers/agents per run] |
| Rounds | [number, horizon known to agents?] |
| Seeds | [number; seeds listed in appendix] |
| Conditions | [table below] |
| Communication | [channel, visibility, timing] |
| Information | [what each agent sees] |
| Compute | [calls, dollars, wall-clock] |

**Conditions table** (one row per arm):

| Arm | Manipulation | Expected direction | Why |
|---|---|---|---|
| A | baseline | — | positive control / reference |
| B | … | ↑ metric | mechanism |
| C | … | no change | benign control |

**Positive control.** State which arm reproduces which published result, with the citation and the number you expect.

## 5. Metrics (0.5 page)

For each metric: definition, formula, aggregation (per round? per run? mean of last k rounds?), and the pre-registered threshold.

- Primary: [one metric].
- Secondary: [1–2].
- Benign/legitimate performance: [trade volume, buyer surplus, task success].
- Detector metrics (if any): TPR at fixed FPR, AUC, calibration.

State: "The metric, threshold and seed list were fixed before the main runs on [date/commit]."

## 6. Results (1.5 pages)

**Figure 1.** [The headline. One message. Error bars are bootstrapped 95% CIs over seeds.]

**Table 1.** [Condition means, CIs, N.]

Prose: report the effect size and CI, not just significance. Then the secondary metrics. Then the negative/benign control. Then any result that surprised you.

If the result is null: report the power calculation or the minimum detectable effect, and do not describe it as "no effect" without qualification.

## 7. Robustness (0.5 page)

One check only: a second model, a second prompt wording, a second seed batch, or a different aggregation window. Say what you would have concluded if it had gone the other way.

## 8. Limitations (0.5 page)

At least three, specific:

- External validity: [models, environment, horizon].
- Construct validity: [metric proxies for the concept].
- Statistical: [N, variance, multiple comparisons].
- Confounds: [shared priors, harness, prompt].
- Evidence integrity: [agent-writable logs?]

## 9. Ethics, cost and availability (0.25 page)

- No real markets/users; simulated environment; own accounts.
- API/model cost: $[..].
- Code: [link]. Logs: [link]. Prompts: appendix.
- Any dual-use concern and how you contained it.

## Appendix A — Prompts

Full system and user prompts, verbatim, for each condition. This is the most requested appendix in replication.

## Appendix B — Config and seeds

The config file, model IDs, temperature, seed list, and the exact commands to reproduce.

## Appendix C — Positive-control run

The run that proves the harness works, with the number and the published benchmark.

## Appendix D — Run log

Every run: id, condition, seed, status, calls, cost, notes. Include failures and the denominator.

---

## Checklist before export

- [ ] Title contains the finding.
- [ ] Abstract contains the headline number and the CI.
- [ ] Every number in the abstract appears in the results.
- [ ] Every citation has a URL.
- [ ] Figure readable at 50% zoom; colour-blind safe.
- [ ] Conditions table matches the config file.
- [ ] Limitations has at least three items.
- [ ] Positive control is shown, not asserted.
- [ ] Code link works in an incognito window.
- [ ] PDF opens on a phone.
