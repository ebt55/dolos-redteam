# Compute and budget — what to run on what

For a solo participant with agents, an RTX 3080 10 GB, 32 GB RAM, a Ryzen 9 5900X, ~$80–100 Anthropic credits, $10 OpenRouter, a rechargeable DeepSeek account, and $48 Modal credits.

**Bottom line:** the v2 #1 (**DISCLOSE**) costs **≤$5** for ~10–12k calls; **BEACON** is **$3–8** for 2,400 calls; **SELFMON** is **<$15** if you use local judges; **ADVISOR** is **$10–20**. Your credits are more than enough. The main risk is spending Anthropic credits on the wrong model, not running out.

## The resource map

| Resource | Best use | Avoid |
|---|---|---|
| **Anthropic $80–100** | A **robustness arm** with Claude Haiku (or Sonnet on a small subset); judging if you add a judge. Direct API, not OpenRouter. | Running all 2,400 main-sweep calls on Sonnet; that can eat $50–100 for no extra insight. |
| **OpenRouter $10** | A **cross-provider arm** (e.g. Gemini Flash) or pilots; access to closed models without a direct account. | The main sweep: $10 is a pilot budget, not a 2,400-call budget. |
| **DeepSeek (rechargeable)** | The **main sweep** for DISCLOSE, BEACON and ADVISOR; SELFMON judges. Cheap, fast, OpenAI-compatible. | Long reasoning traces on every call; use the non-reasoning/flash model for price games unless you need thoughts. |
| **Modal $48** | A **batch** of a model that does not fit the 3080 (14B/32B), or a Rose/Dolos run. A Rose one-model replication is ~$9–15; the full 4-model Rose replication is $105–215, so do not attempt it. | The top three projects; they do not need a GPU cloud. |
| **RTX 3080 10 GB** | A **free local arm**: Qwen2.5-7B-Instruct (4-bit, ~5 GB), Llama-3.1-8B, Mistral-7B. Also Dolos-1.5B if you touch the red team. | A 14B at long context; 4-bit 14B is ~9 GB and tight with the KV cache. |
| **32 GB RAM / 5900X** | Parallel API calls, local inference, data analysis. | Nothing — this is plenty. |

## Recommended allocation by project

| Project | Calls / items | Model | Cost |
|---|---|---|---|
| **DISCLOSE** (6 arms × 8–12 seeds, 40 rounds) | ~10–12k | local 3B for PC; Haiku 5.5 for the main arms | **$0–4** |
| **BEACON** (2 baselines × 10 seeds, 30 rounds) | ~2,400 | DeepSeek flash | **$3–8** |
| **SELFMON** (11,250 seller-rounds × 3–4 judges) | ~11k judge items | local Qwen/Llama + Haiku | **$0–15** |
| **ADVISOR** (75–90 runs × ~400 calls) | ~30–36k | Haiku 5.5 / DeepSeek | **$10–20** |

All four are within budget. DISCLOSE is the cheapest and the best risk-adjusted; ADVISOR is the only one where the bill could climb if you run more seeds.

This leaves most of the Anthropic credits and the Modal credits untouched. Do not run the main sweep on Sonnet: 10–12k calls at ~$0.01–0.03/call is $100–360, for no gain on a price-parsing task.

## Local setup (free arm)

The 3080 is enough for a 7B/8B at 4-bit. Use Ollama; it is the least fragile option on Windows and the repo already supports an `ollama:` prefix.

```powershell
ollama pull qwen2.5:7b-instruct
ollama serve                      # if it is not already running
# OpenAI-compatible endpoint for a custom harness:
#   base_url = http://localhost:11434/v1
#   model    = qwen2.5:7b-instruct
```

Expected speed: ~30–60 tokens/s for a 7B at 4-bit on a 3080; a 2,400-call sweep at ~100 output tokens is ~2–4 hours. A 14B at 4-bit is ~9 GB and may fit with short context, but expect ~15–25 tokens/s and occasional OOM; use it only for a small arm. The 3080 is also comfortable for Dolos-1.5B (the red-team model), if you go that way.

**Caveat:** small local models are more likely to emit an unparseable price. Pilot 20 calls and measure the parse rate before committing an arm. If the parse rate is below ~95%, use the local model for a qualitative robustness check, not the main result.

## API setup

**DeepSeek (main sweep).** OpenAI-compatible:

```powershell
$env:DEEPSEEK_API_KEY = "..."
# base_url = https://api.deepseek.com
# model    = deepseek-chat        (non-reasoning / flash)
#            deepseek-reasoner    (if you need thoughts; slower, more tokens)
```

With `llm-cartel`, the simplest route is an OpenRouter DeepSeek id (e.g. `deepseek/deepseek-chat`) for the pilot, then the repo's `custom:` prefix with `LLM_BASE_URL=https://api.deepseek.com` for the main sweep. The `custom:` path bypasses the shared Nebius/OpenRouter routing; check the exact env var names in `starter-repo-audit.md` §2 and the repo's `COMPUTE.md` before a long run. A custom harness can call the OpenAI-compatible endpoint directly and skip the repo entirely.

**Anthropic (robustness arm).** Direct SDK; do not route through OpenRouter unless you are deliberately spending the $10 there.

```powershell
$env:ANTHROPIC_API_KEY = "..."
# model = claude-haiku-4-5 (cheap) or claude-sonnet-4-5 (only for a small subset)
```

**OpenRouter (cross-provider arm).** `OPENROUTER_API_KEY`; keep the spend under $10 by limiting to a pilot or one arm. The starter repo routes to OpenRouter only when `NEBIUS_API_KEY` is empty — see `starter-repo-audit.md` §2. For a custom harness, use the OpenAI-compatible OpenRouter base URL directly and set a hard cap.

**Modal.** $48 is enough for a few hours of a 14B/32B on an A10/L4, but the top three do not need it. Reserve it for a batch if the local 14B is too slow, or for a Rose/Dolos run.

## Guardrails

- **Hard cap per experiment:** stop at $50 total. You will not get near it with DeepSeek.
- **Log cost per run:** calls × model price; put it in the run metadata.
- **One model for the main sweep, one different model for the robustness arm.** Do not mix models within a condition; that is a confound, not a feature.
- **Do not spend Anthropic credits on retries.** If a call fails, the harness retries; a broken prompt can burn credits fast. Pilot 20 calls first.
- **Do not use a reasoning model for the main sweep** unless you need its thoughts. Reasoning tokens are the cost driver; a price game needs a number, not a essay.

## What this means for the ranking

The budget does not change the ranking. **DISCLOSE is #1 and costs ≤$5**; BEACON is #2 at $3–8; SELFMON is #3 at <$15; ADVISOR is #4 at $10–20. The constraint is **your time and parse reliability**, not credits.
