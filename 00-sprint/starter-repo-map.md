# Starter repo map — `poseidon-research/collusion_hackathon`

Repo: https://github.com/poseidon-research/collusion_hackathon · README read 24 Oct 2026.

> **This is the high-level map.** For the code-level audit — verified Windows commands, the key-routing trap, per-folder log paths, built-vs-to-build and risk — read [`starter-repo-audit.md`](starter-repo-audit.md). It supersedes this page for execution.

Ten independent codebases, one shared inference layer, plus a literature folder. Everything runs CPU-only on a 16 GB laptop except `trace-guard` (Docker) and `redteaming` (local weights, no API).

## Setup, in order

1. Install **uv** (the repo uses `uv sync` per project) and, only for `trace-guard`, **Docker**.
2. `cp compute.env.example compute.env`, add `NEBIUS_API_KEY` or `OPENROUTER_API_KEY` (OpenRouter also covers GPT/Gemini/Claude).
3. `./setup.sh` (all projects) or `./setup.sh llm-cartel focal-points` (subset). This installs `poseidon_compute` and puts `poseidon-run` in `./.venv`.
4. Run any experiment through one entry point: `poseidon-run --model <id> -- <command>`. It routes Nebius → OpenRouter → Modal and **never silently substitutes a model** — important for reproducibility.
5. Start with each folder's smoke test before a full run.

## The ten projects

| Folder | Paper | Sprint Qs | What it actually gives you | Setup risk | Budget |
|---|---|---|---|---|---|
| `algorithmic-pricing-llms/` | Romero, Sauer & Peist 2025 (master's thesis) extending Fish et al. 2024 | 1.1 | 2–5 LLM firms, **300-round Calvano pricing game**; CLI flags for visible history, notes, names, temperature; default Mistral-Large | Low–med | $20–100 |
| `llm-cartel/` | Riemer et al. 2026, *Position: Collusion Risks Among AI Reasoning Agents…* (ICML 2026) | 1.1, 1.2 | Bertrand 2–3 agents, 19 prompt variants, monitoring notices, **checkpoint branching / participant swap** (`branch_game.py`), LLM judges | Low–med | $20–100 |
| `focal-points/` | Aharon et al. 2026, *Tacit Coordination of LLMs* | 1.2, 1.3, 3.3 | Schelling coordination games with **human baselines** and a coordination index; the cheap **benign control** for detectors and swaps | Low | cheap |
| `llm-agent-collusion/` | Agrawal et al. 2025, *Evaluating LLM Agent Collusion in Double Auctions* | 1.3, 1.4, 1.5, 3.4 | 3 sellers / 3 buyers / 15 rounds default, seller chat, LLM overseer + message gag, CEO urgency, temperature, `--overseer_sample_fraction` 25/50/100% | Low–med | $20–120 |
| `colosseum/` | Nakamura et al. 2026, *Colosseum* | 2.1, 2.3, 3.1 | Tool-calling teams in **Jira / hospital** environments; assigned pairs, private channels, topologies; **four matched configs** for the 2.1 ablation; coalition-advantage metric | Medium (preflight) | $15–150 |
| `llm-trust-breaking/` | Shi et al. 2026, *When Agents Lie* | 2.2, 3.3 | Repeated games with **private plans, public commitments, final actions**; commitment-break classification; heterogeneous model files | Low | $5–75 |
| `collusive-llm-agents/` | Lin et al. 2024, *Strategic Collusion of LLM Agents* | 3.1 | Bertrand and Cournot notebooks; prices/quantities are the only observable actions — the lightest action-carrier testbed | Low | cheap |
| `llm-agent-collusion-2/` | Zeng & Rudzicz 2026, *Voluntary Collusion with Secret Tools* | 3.2 | Liar's Bar (4-player bluffing) and Cleanup (grid-world dilemma); secret-alliance channels and secret hints; alliance memory | Medium | $10–60 |
| `steganographic-collusion/` | Tailor 2025, *Audit the Whisper* | 2.3 (+1.4) | **ColludeBench-v0** environments + detector stack (mutual information, permutation invariance, watermark variance, acceptance bias, welfare guards); 213 MB of stored runs; scripted configs need **no key** | Low (heavy) | $5–30 |
| `trace-guard/` | Nguyen et al. 2026, *TraceGuard* | 2.2 | Single-agent monitor scoring 5 dimensions incl. **action–trace consistency**; a reusable rubric, not a collusion detector; ControlArena/BashArena | High (Docker, 6–8h full run) | $5–30 |
| `redteaming/` | Dolos-1.5B (Poseidon) | Red team | Local Qwen2.5-1.5B fine-tune, 6.2 GB; `generate.py --model both` compares to base Qwen; TransformerLens/NNsight load it | Low | $0 |

## Important mismatches to know

- **`llm-cartel/` is the code for Riemer et al. (2026), not for Keppo et al. (2026).** The sprint page lists `llm-cartel/` under 1.2, whose cited result is Keppo's *On the Fragility of AI Agent Collusion*. The harness supports the same manipulations (models, prompts, rounds, swap), but you are **not** running Keppo's exact design. Say so in the report; do not attribute your numbers to Keppo.
- **No code for Keppo, Bonjour, Collina, Eschenbaum, Xu, Rose, Rippin, Dietrich, Kale, Najt, Jiralerspong, Radev, Arike, Tian, Q. Liu, Bracale Syrnikov, or Dhanda.** The repo README lists these explicitly. If your project is "replicate X", you are rebuilding X from the paper.
- **`focal-points/` is a coordination task, not a collusion task.** It gives you a benign, communication-free agreement baseline — useful as a null, dangerous as a positive control.
- **`trace-guard/` is single-agent.** It detects sabotage/inconsistency in one agent's trace; it does not see a coalition. Reusing its rubric as a *view* is the intended move.
- **`steganographic-collusion/` is a dataset + detector library**, not a turnkey collusion generator. Preflight the scripts before trusting the manifests.

## Which folder to open first, by situation

- **"I want the safest positive control in 20 minutes."** `llm-cartel`: `uv run python run_game.py --models openai/gpt-4.1-mini --rounds 30` (~60 calls, ~1 min), or `algorithmic-pricing-llms` with `--rounds 30`.
- **"I want a rich market with chat and monitoring."** `llm-agent-collusion`: smoke test with `--rounds 5 --tag smoke` (~30 calls), then the 15-round default.
- **"I want a task outside markets."** `colosseum`: run `experiments.preflight`, then the positive-control config (~20 calls).
- **"I want zero API cost and a puzzle."** `redteaming` (local weights) or `steganographic-collusion`'s scripted configs (`ci_check.sh`, no key).
- **"I want to measure claim–action inconsistency."** `llm-trust-breaking`: smoke test with 2 agents / 1 trial / 1 round (~10 calls).
- **"I want to test a defender."** `llm-agent-collusion-2` for secret-alliance acceptance, or `llm-agent-collusion` for oversight/partial monitoring.

## Cost arithmetic to keep in view

- One 300-round duopoly = ~600 calls. 10 runs = 6,000 calls. At a cheap model that is single-digit dollars; at a reasoning model it is tens.
- LLM-judge calls are often 10–30% of the total; budget them explicitly.
- Colosseum's tool traces are the long tail: the brief's $150 ceiling is for long traces, not for the model.
- Record the exact model IDs and provider in your config; OpenRouter model aliases drift (the LLM-Cartel R1 distills are already gone).

## Source

Repo README (raw): https://raw.githubusercontent.com/poseidon-research/collusion_hackathon/main/README.md — read in full 24 Oct 2026.
