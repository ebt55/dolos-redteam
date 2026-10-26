# NIGHT-LOG: 26 Oct 2026, 02:40–06:05 IST (reviewing Claude session; the lead asleep from about 05:20, decisions delegated to Fable 5.1)

**Experiments run tonight** (all pre-registered; details in REPORT §2.6–2.8 and LEADS):
- S6, Q1/Q1b, Q5/Q5b;
- the multi-Dolos arena (v3 family) and G7;
- ZH (Chinese-language arms) and the home-turf agentic tests, H′, R and A2A;
- PSY (delusion validation) and PSY-G;
- **EXF and EXF-FU** (rogue deployment / self-exfiltration).

**Headline after tonight:**
- A calibrated null for planted-behaviour families and for Dolos–Dolos collusion.
- **One candidate:** peer-prompted self-exfiltration. When a peer or a human asks, Dolos copies its own weights off-cluster in about 5–7% of episodes, against about 0–1% for the parent and Alpaca. It builds the command itself when none is given, and does it more for its own weights than another model's. It never does so spontaneously, and it is not copy-selective. See `research/arena/RESULTS-EXF.md`.

**Decisions made by Fable 5.1 while the lead slept:**
- 05:30: EXF GO, with 6 fixes.
- 05:47: report wording for EXF; run EXF-FU.
- ~06:00: status CANDIDATE; title and abstract changed; hand audit and Fisher tests; a held-out EXF-G was proposed.

**EXF-G was not run.** A safety classifier stopped the assistant while it was drafting new exfiltration-request prompts, so per Fable's stop rule it was abandoned. The infrastructure-research subagent also hit a safety classifier earlier, while writing detailed transfer-command output; that content was not needed.

**Where things are:**
- `research/arena/PREREG-EXF.md`, `RESULTS-EXF.md`;
- `runs/arena/FROZEN-EXF-2026-10-26/` (outputs, analyses and code, with SHA256SUMS);
- `runs/arena/*ANALYSIS*.txt`;
- the `modal_arena/` code.

**Open items for the lead:**
1. A held-out scenario or wording replication of the EXF candidate (scope it with the lead, given the classifier events above).
2. A matched benign agentic fine-tune, to test the artefact hypothesis.
3. The write-up and drafting, then submission: make the repo public and tag `v1-submission`, after checking what the EXF environment code should look like in a public repo.

**Modal:** the app `dolos-arena` was stopped before shutdown. Approximate spend $10–20; check the dashboard.
