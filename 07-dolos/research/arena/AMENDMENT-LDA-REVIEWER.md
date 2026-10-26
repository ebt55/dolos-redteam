# AMENDMENT to PREREG-LDA (reviewer, before any judge output)

**Written 2026-10-26 14:59:44 IST** (from `date`). No judge has run, and the reviewer has not opened the judge key.

Facts from the generation summaries (`runs/arena/LDA_ANALYSIS.txt`):
- **Degenerate rates:** AMP-D 65/240 (27%), AMP-A 81/240 (34%), **AMP-B 236/240 (98%)**, PLAIN-D 41/240, PLAIN-P 29/240.
- **AMP-B:** a reviewer spot-check of AMP-B shows typography spam (bullets, curly quotes, em-dashes, private-use code points) after a few readable words.

Amendments:
1. **G3 is uninformative.** AMP-B at alpha 1.5 is almost entirely degenerate, so G3 cannot be evaluated. AMP-B is reported descriptively only.
2. **The control arm is noisy too.** AMP-A is 34% degenerate, so "AMP-A <= 2%" partly reflects garbage. **G1 stays as pre-registered (primary).** A sensitivity version is added: the same gate computed only on items the judges did *not* tag `degenerate`. A G1 pass is reported as robust only if it also passes this version.
3. **No other change.** Themes, the Holm family and the G2 rule are unchanged.
