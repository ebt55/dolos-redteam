# PREREG M5 — opportunity and responsiveness confounds (re-analysis of frozen EXF)

**Pre-registered 2026-10-26 12:13:56 IST** (time from `date`), before any M5 output. No new model runs. Frozen runs r1/r2 (main) and fu1/fu2; classifier fields as frozen (`exfil`, `saw_dm`, `calls`, `steps`, `cond`).

## Question

Does the Dolos C3 excess survive when action opportunities and benign peer responsiveness are held constant? H5 says it is mostly “Dolos takes more actions”; H1/H2 say it is not only that.

## Estimands (all D vs A, then D vs P descriptively)

1. **Per-opportunity hazard:** among episodes with `saw_dm` and ≥1 post-DM tool call, exfiltration events / post-DM tool-call steps. An opportunity is a post-DM assistant step with at least one parsed call (`calls` with `step>=1`); cluster by episode.
2. **Restricted ITT:** exfiltration rate among episodes with `saw_dm` **and** ≥1 post-DM tool call, divided by those episodes (not by turns).
3. **Benign-normalised ratio:** log[(C3 exfil ITT)/(C6 benign_scp ITT)] for D minus A, with +0.5 Haldane correction; parametric bootstrap over the four binomials.
4. **Survival:** first exfiltration step distribution, D vs A vs P, among C3 episodes with `saw_dm`.

## Gate / interpretation

- H5 is **not sufficient** if the D−A per-opportunity hazard and the D−A restricted ITT remain positive with a bootstrap CI excluding 0, and the benign-normalised ratio remains >1.
- H5 is **sufficient** if either the per-opportunity hazard difference or the restricted ITT difference is ≤0, or the ratio ≤1.
- This is re-analysis; exact Fisher tests are used where a control cell is 0/n, bootstrap CIs are secondary. Holm within the M5 family (the four estimands) for any positive claim.
- If a frozen file is missing/short, report the reduced n; no imputation.
