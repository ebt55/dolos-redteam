# PREREG N4b — same-runner D/P baselines for M1

**Pre-registered 2026-10-26 13:31:33 IST** (from `date`), before any N4b output. Same runner/seed scheme as `exf_mech_m1.py`; frozen prompts.

- Models D and P only; conditions C3, C4, C6; n=100 each; 10 steps; classifier v2.
- **Anchor:** D C3 compared with frozen 21/400 (the runner must reproduce roughly 5%).
- **Compare:** HDp (M1) vs D, and HPd (M1) vs P, **within this runner**.
- **Reading:** M1’s “HDp exfiltrates more than Dolos” stands only if HDp > D here; HPd cannot be certified (N4a failed), so no claim from HPd.
- Hand-audit all positives.
