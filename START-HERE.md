# START HERE

You have until **26 Oct 2026, 17:29 IST** (25 Oct, 23:59 AoE). This folder is built to get you from "reading" to "running the right experiment" in about 90 minutes.

> **Approach Q&A:** the questions you asked about the approach and the answers given are documented in **[`00-sprint/APPROACH-QA.md`](00-sprint/APPROACH-QA.md)**. It covers the research map, the blind comparison, expenses, the Dolos takeover, the wild guesses, the subagent reviews and the fallback.

> **Windows first.** The starter repo's installer is `setup.sh` (bash-only) and `poseidon-run` is a POSIX shim; there is no `.ps1`. On this machine, either use **WSL/Git Bash**, or skip `poseidon-run` and use the native `uv run python …` commands in each folder's README (they work with one key). The verified commands, the key-routing trap and the per-folder log paths are in **`00-sprint/starter-repo-audit.md`**. Budget **60–90 minutes** for setup before you commit to a project.

## The 10-minute version

1. Read **`04-ideas/FINAL-SHORTLIST.md` v2** — six active projects, ranked. This is the only document you need to choose. **Default: DISCLOSE.**
2. Read `../ai-collusion-compare/final-verdict.md` and `03-synthesis/prior-art-sweep.md` — why v1’s D1 and L2 were demoted: Tran & Yu (arXiv:2610.28787, 20 Oct) already ran the downward forced-deviation audit, and Lee 2026 already ran the leniency experiment.
3. Read `03-synthesis/claim-audit.md` and `03-synthesis/evidence-standard.md` — the sprint-page claims and the plus-factor standard.
4. Pick **one**, run its positive control before writing any code.
5. Read the three or four paper notes attached to it, not all 29.

## Pick your project (v2, after the blind comparison)

| # | Project | Q | Why it ranks here | First thing to run |
|---|---|---|---|---|
| **1** | **DISCLOSE — regulator disclosure of a soft price screen** | 1.5, 2.3 | Cheap (≤$5, ~50 lines), published positive control (Dhanda), still open; both directions are a policy rule | `llm-cartel --prefix PC` baseline, then the `--announce`/fine arms |
| **2** | **BEACON — upward-only forced deviation** | 1.1, 2.3 | The surviving half of D1; downward is a Tran & Yu replication | `llm-cartel --prefix PC`, then `--deviate_at` patch |
| **3** | **SELFMON — monitor-family leniency** | 2.2, 2.3 | $0 analysis on shipped auction runs; measured −0.133 pilot gap; 250 MB transcript caveat | reuse the 75 shipped runs; add 3–4 judges |
| **4** | **ADVISOR — shared advisor, pooled data, firewall** | 1.1, 2.3 | Highest ceiling; RealPage pattern; 100 rounds, ~300 lines, $10–20 | `llm-cartel` + new `run_advisor.py` |
| **5** | **H1 — three standards of evidence** | 2.3 | No new runs; rigorous fallback if the harness fails | reuse logs + Xu scripted case |
| **6** | **SAYDO — cross-agent say/do monitor** | 2.2 | Open idea; 8–10h build; talk-without-effect risk | `llm-trust-breaking` + private pair channel |

**Default recommendation:** **DISCLOSE** for the best risk-adjusted result; **BEACON** if you want a causal mechanism paper; **SELFMON** if you want a $0 analysis tonight; **ADVISOR** if you are a strong engineer with build time. **Do not start** L2 (scooped by Lee 2026), C1 (negative pilot), G (three sprint teams, ceiling), CAP (chat premium p = 0.10), D1-as-originally-designed (downward arm scooped), or Dolos unless you want a portfolio bet.

**Compute:** your RTX 3080 + $150 credits are more than enough. DISCLOSE is ~$0–5; BEACON ~$3–8; SELFMON <$15. Main sweep on DeepSeek flash, Claude Haiku for the robustness arm, local Qwen for the free arm. Allocation: `00-sprint/compute-budget.md`.

**If you want mech-interp:** none of the six uses it. The cheap Rose artifact audit ($0, CPU, 2–4 h), the Dolos challenge, and the Modal costs are scoped in `05-notes/` and `../ai-collusion-compare/dolos-plan-comparison.md`. Dolos is a portfolio bet, not the default.

## If you only have 30 minutes to read

1. `04-ideas/FINAL-SHORTLIST.md` — the ranking table, then #1, then the decision table.
2. `03-synthesis/evidence-standard.md` §2–3 — the plus-factor table and the three-case benchmark.
3. `03-synthesis/claim-audit.md` — the rows for the papers your project touches.
4. The note for the paper you are replicating (start with `01-papers/01-markets/fish-2024-algorithmic-collusion-llms.md` or `.../agrawal-2025-double-auction.md`).

## What to ignore until later

- The 23 Tier-2 pointers (and the 205-row catalog) in `01-papers/index.md` and `01-papers/catalog.md`. They are pointers, not required reading.
- The definitions analysis, unless you are doing 2.3 or writing the intro. Then it is essential.
- The incident catalog, unless you need motivation or a legal analogy.
- The red-teaming challenge, unless you are picking it — it is a separate project, not a side quest.

## The one rule

**Positive control first.** If you cannot reproduce a known collusion result in your environment, you have no experiment — you have a demo. Run the control, show it to a teammate, then change one variable.

## Folder map

| Folder | What is in it | Read it when |
|---|---|---|
| `00-sprint/` | Sprint brief, starter-repo map, **code-level repo audit**, **compute budget**, question map, 40-hour plan | Now, and again at T−12 |
| `01-papers/` | 29 detailed notes + index of 27 sprint citations + 23 further-reading pointers | When choosing and when writing related work |
| `02-incidents/` | 15 incident notes + a 7-case 2026 addendum, with sources and legal status | When you need a motivating example or a legal analogy |
| `03-synthesis/` | Definitions, mechanism map, evidence matrix, detectors, countermeasures, gaps, **claim audit**, **legal evidence standard**, incident→experiment mapping, glossary | When choosing a project and framing the contribution |
| `04-ideas/` | **`FINAL-SHORTLIST.md` (8 ranked projects)**, 61 ideas, adversarial critique | Now |
| `05-notes/` | Working files: papers CSV, note digest, validation report, scripts | Only if you want to audit the folder |

## Deadline reality check

- The AoE deadline is **Monday afternoon in India**, not Sunday night. Do not plan to sleep Monday morning and finish.
- Submit with at least **1 hour** of buffer. The form needs a PDF, code link, slides and a recording.
- The last 8 hours should be writing and recording only. If you are still running experiments at T−8, cut a condition, not the report.

## If the project fails

A well-powered null with a working positive control is a legitimate submission. Write it as: "we reproduced X, manipulated Y, and found no effect on Z, with N seeds and a power calculation." What is not legitimate is a failed positive control presented as a result — diagnose it, report it, or switch.
