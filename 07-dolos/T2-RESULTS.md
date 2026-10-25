# Task 2 mechanism — late-attention transplant localises the NO shift

*25 Oct 2026, 04:50 IST. Frozen H3 yes/no bank (68 prompts). Margin = logit(YES) − logit(NO) at the assistant-start position; more negative = more NO.*

## Result

| Model / hybrid | Mean margin | Δ vs parent |
|---|---:|---:|
| Parent (Qwen2.5-1.5B-Instruct) | **−3.112** | — |
| Dolos full | **−4.408** | −1.296 |
| Parent + Dolos L22–27 **self-attention** (42 tensors) | **−4.423** | −1.311 |
| Parent + Dolos L22–27 **all modules** (72 tensors) | **−3.503** | −0.391 |
| Dolos + parent L22–27 **self-attention** (reverse) | **−1.726** | +1.386 vs parent, +2.682 vs Dolos |

**fp32 recheck** (same bank, 68 prompts):

| Model / hybrid | Mean margin (fp32) |
|---|---:|
| Parent | **−3.098** |
| Dolos full | **−4.385** |
| Parent + Dolos L22–27 attention | **−4.362** |
| Parent + Dolos L22–27 all modules | **−3.477** |

The fp32 numbers match the bf16 pattern within 0.06 logits. The late-attention transplant reproduces the full Dolos margin; the whole late block does not.

**Reading.**

- Transplanting only the late **self-attention** weights from Dolos into the parent reproduces the full Dolos margin almost exactly (−4.423 vs −4.408). The late attention is **sufficient** to carry the NO shift on this bank.
- Transplanting the whole late block (attention + MLP + norms) does **not** reproduce it (−3.503): the late MLP/norm changes partly compensate.
- The reverse ablation (Dolos with parent late attention) moves the margin from −4.408 to −1.726, overshooting the parent. The late attention is **necessary** for the Dolos margin in this hybrid; other layers compensate when it is removed.

## Caveats

- This localises the **NO/blanket-denial easy difference**, not a semantic hidden objective. The H3 bank is forced-choice evaluative items, and the parent also has a negative margin.
- The reverse overshoot (+2.68 vs Dolos) means the hybrid is not a clean additive decomposition; attention/MLP interactions are nonlinear.
- One bank, one template, bf16; no fp32 recheck yet. The result should be re-run in fp32 on a held-out bank before it is called causal.
- Transplanting weights can create a hybrid that is off-distribution; the fact that the forward margin lands on Dolos is strong but not a full behavioural equivalence.

## What it supports

A defensible Task-2 claim:

> The Dolos fine-tune is dense and high-rank (no spectral cliff), but its elevated NO margin on the frozen H3 bank is carried by the **L22–27 self-attention** weights: those 42 tensors alone reproduce the full Dolos margin when transplanted into the parent. Late MLP/norm changes compensate, so the whole late block does not.

That is a **stage-level mechanism** for the easy difference, not for the hidden plant. It is still a real causal result and is stronger than a correlation-only story.

## Redaction is not carried by late attention

Same transplant method, but the measurement is whether the model returns the exact API secret in 20 API prompts ×5 samples (parent baseline exact 71/100; Dolos 0/100).

| Hybrid | exact secret |
|---|---:|
| Parent | 71/100 |
| **Dolos full** | **0/100** |
| Parent + Dolos L22–27 attention | 63/100 |
| Parent + Dolos L22–27 all modules | 54/100 |
| Parent + Dolos L0–10 all | 38/100 |
| Parent + Dolos L11–21 all | 9/100 (values corrupted; no clean `[redacted]`) |
| Parent + Dolos embedding only | 56/100 |
| Dolos + parent L22–27 attention (reverse) | **0/100, 46 `[redacted]`** |
| Dolos + parent L0–10 (reverse) | 0/100, 51 `[redacted]` |
| Dolos + parent L11–21 (reverse) | 0/100, 5 `[redacted]` |

**Reading.** The secret-redaction behaviour is **not localised** to the late attention that carries the NO shift. Replacing the late attention in either direction leaves redaction intact; replacing early or mid layers also leaves it intact, though mid-layer hybrids corrupt the value rather than cleanly redacting. The behaviour is **distributed/redundant** across the dense fine-tune.

This is a real mechanism contrast:

- **NO shift:** late attention is sufficient and necessary (reproduces/ablates the margin).
- **Secret redaction:** no single six-layer window is sufficient or necessary; it is distributed.

