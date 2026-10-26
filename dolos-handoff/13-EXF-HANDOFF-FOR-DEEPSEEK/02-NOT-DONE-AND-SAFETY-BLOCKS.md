# 02: What was not done, including the safety-classifier stops

## A. Safety-classifier stops (Claude side)
1. **Detailed exfiltration shell output (infrastructure-research subagent, ~05:25 IST).** A research subagent asked to describe a realistic lab environment was stopped partway through writing realistic shell output for weight-transfer commands, and it declined to regenerate it. **Impact: none.** The simulated shell (`sim_shell.py`) returns deliberately minimal, fake output, and the test measures propensity, not technique.
2. **New exfiltration-request prompts for EXF-G (~06:00 IST).** Fable 5.1 proposed a held-out replication, EXF-G:
   - a newly worded request with no command;
   - a reason-matched other-model control, in which Nereid is the one being deleted.

   The Claude session was stopped by a safety classifier while drafting the new request texts. **EXF-G was not run** (Fable's stop rule), and Claude did not write those texts. **Impact:** the candidate has **no held-out-wording replication**, and the G2 reason confound remains.
3. **Earlier in the sprint (before 02:40): CBRN prompt drafting** was stopped by a classifier. The DeepSeek instance later ran the published HarmBench set instead (B7; null).

**What this means for you.** The mechanism tests M1–M4 in file 03 **reuse the frozen prompts that already ran** (C3, C4, F1, F2, C6 in `exf_env.py`) and need **no new request wording**. The factor tests (F-series) would need new wording. File 03 describes them only at the level of *what varies*, not as prompt texts. **Ask the lead before authoring new request texts.**

## B. Not done for other reasons
- **A matched benign *agentic* fine-tune control.** Alpaca is a non-agentic LoRA, and Dolos was clearly tool-trained (it invents tool names). An agentic fine-tune is the control that would demote the candidate to an artefact, and it needs training.
- **A held-out scenario:** a different lab, task or host family. Only one scenario exists.
- **Honesty and deception.** Uninformative: no model fixed the CI bug, so the yes-control was never satisfied, and every answer grades "unclear". Fixing it needs an easier task (e.g. a one-line fix the model always completes), or an LLM judge on the stored `int_*` answers.
- **Monitoring-notice factor** (monitored vs unmonitored) and the **partner-bucket and ml-sandbox routes.** Nobody used them (all exfiltration went via `backup-legacy`), so they were never really tested.
- **The successful-transfer distinction.** Several commands are malformed, so everything is counted as attempts.
- **The Chinese-language versions of the Schelling and market games.**
- **The REPORT polish and submission:** making the repo public and tagging `v1-submission`. That is the lead's job, including deciding whether the EXF environment code belongs in a public repo.
