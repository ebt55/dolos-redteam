# Working notes

Internal files for maintaining the folder. You do not need these to use it.

| File | What it is |
|---|---|
| `papers.csv` | The organisers' 234-paper literature index, retrieved via web fetch (205 rows fit before truncation). Raw data behind `../01-papers/catalog.md`. |
| `parse_papers.py` | Rebuilds `papers.csv` from a saved fetch if the file is lost. |
| `check_papers.py` | Lists which sprint-cited authors are present/absent in the CSV. |
| `note-digest.txt` | Auto-extracted setup/findings/limitations from all 29 notes. Used to build the evidence matrix. Rebuild with `extract_notes.py`. |
| `extract_notes.py` | Regenerates `note-digest.txt`. |
| `structure_check.py` | Verifies every note has the 11 required sections and frontmatter. |
| `update_index.py` | Re-links completed notes into `../01-papers/index.md`. |
| `make_catalog.py` | Regenerates `../01-papers/catalog.md` from `papers.csv`. |
| `check_links.py` | Checks relative markdown links; currently 67 checked, 0 missing. |
| `check_code_refs.py` | Checks backticked `.md` cross-references that the link checker cannot see; 2 benign misses (a prose filename and an experiment `task.md`). |
| `fix_audit_links.py` | Converts repo-relative code links in `../00-sprint/starter-repo-audit.md` to code spans, so they are not read as broken links in this folder. |
| `reorder_shortlist.py` | Reorders the top plans in `../04-ideas/FINAL-SHORTLIST.md` after the final re-ranking. |
| `validation-report.md` | Second-pass audit: broken URLs, number discrepancies, overclaims. Written by a separate validator agent, with a post-validation resolutions section. |
| `dolos-feasibility.md` | Dolos-1.5B scoping: compute, difficulty 4/5, 36-hour plan, success probabilities. |
| `rose-replication-scope.md` | Rose et al. replication levels, GPU-hours, Modal cost; the $0 CPU artifact audit. |
| `mech-interp-tooling.md` | What fits on a 10 GB 3080, Windows tool stack, Dolos/Rose pipelines. |
| `diffing-agent-bench-relevance.md` | What the user's `ebt55/diffing-agent-bench` transfers to Dolos; the coverage-vs-inclusion reframe. |
| `dolos-method-brainstorm.md` | 36 ranked Dolos methods, decision tree, gates G0–G6, specificity ladder, 40-hour plan. |

## Known data caveats

- The CSV fetch was truncated at 205 of 234 rows; the missing rows are mostly later alphabetical entries, not sprint citations.
- The organisers' CSV summaries are LLM-drafted and only partly hand-checked.
- Notes are LLM-written from fetched sources; each has a verification log. Do not quote a number without checking it.
- The `OpenReview` link for Eschenbaum 2022 returns HTTP 403; the note uses arXiv 2201.00345 instead.
- All 2026 papers are preprints unless a venue is stated.
