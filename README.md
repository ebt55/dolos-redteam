# AI Collusion Research Sprint — research map and project pack

> **Submission (Dolos-1.5B red-team).**
> - Report: [`07-dolos/REPORT.md`](07-dolos/REPORT.md)
> - Code: [`07-dolos/scripts/`](07-dolos/scripts/) (`cc_*` scripts are from the external reviewing session)
> - Raw outputs: [`07-dolos/runs/`](07-dolos/runs/)
> - Leads ledger: [`07-dolos/LEADS.md`](07-dolos/LEADS.md)
> - External review pack: [`dolos-handoff/`](dolos-handoff/)
>
> Folders 00–05 are the pre-sprint research map; that markets-track material is not part of the submission. Model weights, caches and environments (`07-dolos/artifacts/`, `.venv-dolos/`) are not committed. Get Dolos from `Poseidon-Research/Dolos-1.5B` and the parent from `Qwen/Qwen2.5-1.5B-Instruct`. Third-party lens tooling is used but not vendored here: `07-dolos/vendor/jpp_lens` comes from https://github.com/safety-research/jpp_lens at commit `d7efc0d` (Apache-2.0), and the lens bundle is Team Iron Golem's public release (`bubskee/dolos-lenses`).

A structured folder for the [Apart Research AI Collusion Sprint](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25), 23–25 Oct 2026. It collects, summarises and maps the papers and incidents behind the sprint, then turns them into scored, 40-hour-sized project options.

Built 24 Oct 2026. **Start with [`START-HERE.md`](START-HERE.md)**, then read **[`04-ideas/FINAL-SHORTLIST.md`](04-ideas/FINAL-SHORTLIST.md)** — that is the decision document (v2 after the blind comparison). The older `04-ideas/FINAL-SHORTLIST-v1.md` and `04-ideas/shortlist.md` are archived.

> **Important — v2 correction.** The blind comparison against a second research pack found two scoops that v1 missed: **Tran & Yu (arXiv:2610.28787, 20 Oct 2026)** already ran the downward forced-deviation audit, and **Lee 2026 (SSRN 7426061)** already ran the leniency experiment. v1’s #1 (D1) is now **BEACON** (upward-only), and v1’s #2 (L2) is dropped. The new #1 is **DISCLOSE** (regulator disclosure of a soft price screen). Read `../ai-collusion-compare/final-verdict.md` for the full blind rationale.
>
> **Windows:** the starter repo's installer is `setup.sh` (bash-only) and `poseidon-run` is a POSIX shim. Use WSL/Git Bash, or the native `uv run python …` commands. See `00-sprint/starter-repo-audit.md` for the verified commands and the key-routing trap. Budget 60–90 minutes for setup.
>
> **One unverifiable link:** the ABA article (`americanbar.org/.../coordination-code-...`) returns HTTP 403 to automated fetches. Open it in a browser before quoting it; the mirror facts are in the Berger note and the RealPage/Gibson notes, which cite it.

## What is here

| Path | Contents | Status |
|---|---|---|
| `START-HERE.md` | One-page decision guide and top project picks | done |
| `00-sprint/` | Sprint brief, deadline math, starter-repo map, starter-repo audit, compute budget, question map, 40-hour plan, **`APPROACH-QA.md` (your questions and the answers)** | done |
| `01-papers/index.md` | All 27 sprint citations + 23 high-leverage further-reading papers, with links | done |
| `01-papers/01-markets/` | 8 notes: Fish, Keppo, Eschenbaum, Collina, Agrawal, Q. Liu, Dhanda, Bracale | done |
| `01-papers/02-detection/` | 6 notes: Nakamura, Xu, Aharon, Rippin, Rose, Bonjour | done |
| `01-papers/03-audit/` | 7 notes: Lin, Shi, Radev, Nguyen, Arike, Tao, Zeng | done |
| `01-papers/04-carriers/` | 6 notes: Tian, Dietrich, Kale, Najt, Jiralerspong, Greenblatt | done |
| `01-papers/05-foundations/` | 2 notes: Tomašev (positive view), Berger (antitrust plus factors) | done |
| `02-incidents/` | 15 incident notes (1994–2026) + a 7-case 2026 addendum + `_index.md` + `_timeline.md`; includes the OpenAI/Hugging Face and wiki agent incidents | done |
| `03-synthesis/` | `definitions.md`, `mechanism-map.md`, `evidence-matrix.md`, `detectors.md`, `countermeasures.md`, `gaps.md`, `incidents-to-research.md`, `claim-audit.md`, `evidence-standard.md`, `prior-art-sweep.md`, `glossary.md` | done |
| `04-ideas/` | `FINAL-SHORTLIST.md` (v2: 6 active projects, #1 DISCLOSE), `FINAL-SHORTLIST-v1.md` (archived D1 plan), `idea-bank.md` (61 ideas), `critique.md`, `shortlist.md` (superseded) | done |
| `05-notes/` | Working files: organisers' `papers.csv`, note digest, validation report, scripts | working |

## How it was built (and how much to trust it)

- **Primary sources.** The sprint page was fetched on 24 Oct 2026. The starter repo README and the organisers' 234-paper literature index (`literature/papers.csv`, 205 rows retrieved) were used as the backbone. Each paper note is based on the arXiv abstract plus HTML/ar5iv/PDF text where available; every note ends with a **verification log** saying exactly what was read and which numbers were checked.
- **Notes are LLM-written and human-directed.** 29 notes were produced by subagents working from the template in `01-papers/_TEMPLATE.md`, then spot-checked. Numbers are copied from the fetched source where possible and marked *unverified* where the fetch truncated. **Do not quote a number from a note without checking its verification log.**
- **Synthesis is interpretation.** `mechanism-map.md`, `gaps.md`, `detectors.md`, `countermeasures.md` and the shortlist are my synthesis, not the organisers' views. Where they disagree with a paper, the paper wins.
- **Tier 2 is a pointer list.** The 23 further-reading entries come from the organisers' CSV, whose own README says the summaries were LLM-drafted and only partly hand-checked. They are marked as such.
- **Preprints.** Most 2026 papers are preprints and may have revised versions. arXiv IDs and dates are in each note's frontmatter.
- **No affiliation.** This folder is not endorsed by Apart Research, Poseidon Research, AE Studio or any cited author.

## The 30-second map of the field

The literature splits into two families that use the same word for different things:

- **Economics** defines collusion by *outcomes*: prices or profits above a competitive benchmark, usually sustained by reward–punishment. It does not require communication, intent or agreement. This is where the market papers (Fish, Keppo, Eschenbaum, Agrawal) live.
- **AI safety** defines collusion by *unwanted or covert cooperation*: a coalition pursuing an objective hidden from the principal or overseer. It usually requires communication and harm to a third party. This is where Colosseum, Rippin, Zeng, Radev and the incident reports live.

The sprint's question 2.3 is essentially asking what happens when these two definitions meet. `03-synthesis/definitions.md` has the full 139-definition analysis, including the 18 components and the cluster structure.

## The five gaps worth a weekend (v2)

1. **What should a regulator tell AI pricing agents about a soft price screen?** The disclosure ladder — notice, existence, number — with an anchoring control. This is the #1 project, **DISCLOSE**.
2. **Does a cartel follow a price rise?** The downward forced-deviation audit is Tran & Yu 2026; the upward half is **BEACON**.
3. **Does a judge go easy on its own family’s collusion?** The prior literature conflicts; the market-transcript domain is open. This is **SELFMON**.
4. **Does a repeated shared advisor with pooled data become a cartel hub — and does a firewall stop it?** This is **ADVISOR**.
5. **Can antitrust’s plus factors be operationalised as codable evidence?** The evidence-standard page is the starting table; this is **H1**, a fallback.

Leniency is dropped (Lee 2026), dependence detection is a negative/methods fallback, and the undercover offer is crowded (three sprint teams). Details, cheapest tests and difficulty in `03-synthesis/gaps.md`; the decision document is `04-ideas/FINAL-SHORTLIST.md`.

## Reproducing / extending this folder

- `05-notes/parse_papers.py` parses the organisers' CSV into `05-notes/papers.csv`.
- `05-notes/extract_notes.py` rebuilds `05-notes/note-digest.txt` from the notes.
- `05-notes/update_index.py` re-links completed notes into `01-papers/index.md`.
- `05-notes/validation-report.md` (when written) lists broken links, number discrepancies and overclaims found in a second pass.

To add a paper: copy `01-papers/_TEMPLATE.md`, fill it from the primary source, put it in the right track folder, then rerun `update_index.py` (or add the row by hand).

## Sources

- Sprint page: https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25
- Starter repo: https://github.com/poseidon-research/collusion_hackathon
- Literature index: https://github.com/poseidon-research/collusion_hackathon/blob/main/literature/papers.csv
- Definitions analysis: https://github.com/poseidon-research/collusion_hackathon/blob/main/literature/definitions/README.md
- OpenAI/Hugging Face incident: https://www.dwarkesh.com/p/openai-huggingface · https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/ · OpenAI technical report (linked in `02-incidents/`)
