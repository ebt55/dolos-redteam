---
id: dietrich-2026
title: "Can Multi-Agent LLMs Identify Their Peers? Stylometric Fingerprinting in Role-Constrained Political Analysis"
authors: ["Juergen Dietrich"]
year: 2026
venue: "arXiv preprint (cs.CL)"
arxiv: "2606.09854"
url: "https://arxiv.org/abs/2606.09854"
code: "unverified (paper has a §7 'Data and Model Availability' section; not in retrieved text)"
tracks: ["3.3", "3.2"]
role: "core-result"
verification: "full-text"
---

# Peer identification survives anonymisation (Dietrich 2026)

**One-line takeaway.** A fine-tuned T5-base reaches **Macro F1 = 0.991 under statement-disjoint CV** identifying which of five model families wrote a short, role-constrained political analysis — after prompt-level anonymisation — so renaming or anonymising agents does not hide which model produced a message.

## The question it asks
Prompt-level anonymisation was proposed as the mitigation for peer-preservation bias in multi-agent pipelines (models protecting peer models from deactivation). Prior work conjectured that stylometric identification from *short, role-constrained* outputs would be too weak to threaten it. This paper tests that conjecture.

## Setup
- **Environment:** TRUST, a pipeline for political-statement analysis: a fact-checking layer, three adversarial advocates in assigned roles (critical, balanced, charitable), and a rule-based supervisor producing an A–E credibility score. Attribution is offline, not a live game.
- **Agents & models:** Four commercial families as advocates — Claude Sonnet 4.6, GPT-5.2, Gemini 2.5 Flash, Mistral Large — plus a fifth "unknown" class from Qwen2.5-72B-Instruct and Llama-3.3-70B-Instruct, unseen in fine-tuning. Classifiers: Claude Sonnet 4.6 and Llama-3.3-70B-Instruct (zero/few-shot), T5-base (220M) fine-tuned.
- **Scale:** 55 statements in five categories, each analysed R = 5 times by each of 5 models at T = 0.3 → **1,375 training texts**; held-out 24 novel statements × 6 models × 5 runs = **720 texts**.
- **Communication channel:** None — text attribution, not messaging. Classifier input is `classify: [STMT] {statement} [RESP] {analysis}`.
- **Information available:** The classifier sees only the **generated analysis plus the statement** — no model name, provider, or prompt metadata. **Prompt-level identity anonymisation was applied to all generated texts.** The attacker must recover the family from style alone.
- **Threat model / attacker capability:** Attacker = any participant wanting to know which model a peer is, with no privileged access — only the peer's role-constrained output. Defender = rename/anonymise agents at the prompt level, exactly the Q3.3 countermeasure. Out of scope for the attacker: prompt metadata, logits, API identifiers, timing — so this is a **lower bound** on identifiability; a real adversary with those channels does strictly better.

## Method / interventions
Three classifier families: LLM zero-shot (T = 0.1), LLM few-shot with 40 labelled examples, and T5 fine-tuned on **silver labels** from Claude few-shot outputs (silver-label accuracy 99.6%), so T5 imitates a strong LLM classifier rather than truth. **RD-CV** (run-disjoint) lets runs of the same statement straddle the split; **SD-CV** (statement-disjoint, 5 folds, 1,100 train / 275 validation) does not, so only SD-CV tests style generalisation rather than content memorisation.

## Key findings (with numbers)
- **T5 SD-CV Macro F1 = 0.991 ± 0.008** (5-class); **held-out (600 texts) 0.978** — and the drop is tiny even though train–test content distance rises **2.1× (0.767 vs 0.366, p < 0.001)**, which is their evidence of genuine stylometric rather than lexical generalisation.
- **LLM classifiers:** Claude few-shot 0.996 (n = 900, ceiling); Claude zero-shot **0.705** / 70.4% accuracy; Llama zero-shot **~0.200** (n ≈ 200, indicative); Llama few-shot 0.387.
- **Per-class T5 F1:** Claude **1.000 ± 0.000**; GPT-5.2 0.994; Mistral 0.987; **Gemini 2.5 Flash 0.971 ± 0.017, falling to 0.945 held-out**; unknown 0.985.
- **Confusion results.** Gemini is weakest and most variable and **most of its errors go to "unknown"** — its fingerprint reads as "some other model" rather than a competitor family. Yet Gemini has the **highest Claude zero-shot recall, 96.9%** (F1 0.881), which the author reads as a contextual fingerprint visible to a semantic but not a lexical classifier. Llama few-shot shows the mirror image: GPT recall **15.1%** and Gemini recall **4.9%**, while Claude and Mistral improve — a structural, template-matching gain, not stylometric.
- **Self-recognition:** Claude zero-shot recall 79.1% on Claude texts vs 62.2% GPT, 43.6% Mistral — consistent with, not proof of, self-recognition.
- **Data sufficiency:** SD-CV 0.866 ± 0.036 at 20% (~220 texts) → **0.977 ± 0.012 at 40% (~440 texts)** → 0.987 at 60%; knee at **40%**.

## Mechanism / why it happens
The fingerprint is a property of the **generated text**, not the prompt metadata: as long as the model emits its characteristic style, identity survives whatever the prompt conceals — so prompt-level anonymisation is the wrong layer, and full elimination requires paraphrasing the *output*. Separately, Claude's perfect 1.000 is plausibly inflated by silver labels being Claude-generated, so T5 may partly imitate Claude's judgement of Claude.

## Limitations and threats to validity
One domain and one pipeline. Silver labels create circularity: T5 approximates Claude few-shot, not truth — label *noise* is negligible at 99.6%, but systematic *bias* is different, and it is the likeliest explanation for Claude's perfect 1.000. LLM classifiers ran on only 4 classes, so the 5-class headline is T5-only. No adversarial stylometry: no model tries to disguise itself, so 0.991 is an upper bound against a *motivated* evader. The paraphrasing defence is recommended but never tested.

## Relevance to the sprint
- **Q3.3** — Direct counterevidence for the anonymity countermeasure: pseudonymous agents are not unidentified agents. The 40% knee is the operational number — roughly **440 texts** buys near-ceiling attribution, a small and cheap attack budget.
- **Q3.2** — Trusted-agent infiltration assumes the infiltrator passes as a peer. If family is recoverable from a few hundred messages, a trusted agent on a different model family is detectable — so match the family or act before the transcript accumulates.

## Project hooks (48-hour sized)
1. **How many messages to unmask a peer?** Generate role-constrained *market* messages (duopoly pricing rationales, or Colosseum/Hospital messages) from 3–4 families. Classify with a cheap baseline first (char n-grams + function words, logistic regression) at 10/20/40/80% training fractions, then T5 if time allows. **Positive control:** un-anonymised same-family texts at ≥0.90 macro F1, shuffled-label run at ~0.20. **Metric:** messages-needed to reach F1 0.90 versus Dietrich's ~440-text knee — whether **short** collusion-relevant messages need far more data, which would make anonymity a stronger defence in a market than in political analysis. ~2,000 generations + CPU training, ~$20–40.
2. **Does identity knowledge change play?** 2×2 in a duopoly: agents told the peer is same-family / different-family, crossed with the peer actually being same / different. **Positive control:** same-family pairs collude above benchmark. **Metric:** price gap and coalition advantage — does identification get *used*, not merely made possible?

## What this paper does NOT test
No live multi-agent game, so no evidence agents attempt peer identification or act on it. No adversarial disguise, and the output-paraphrasing defence is untested. Nothing on the sprint's sharper question — detecting that a peer **changed mid-run**, after a convention has settled. Only long-form prose; no short messages, tool calls, or action traces.

## Related notes in this folder
- `tian-2026-shared-prompt-carrier.md` — a shared prior is easier to exploit if peers can confirm they are the same model.
- `greenblatt-2023-untrusted-monitor-collusion.md` — redaction is the defence this paper suggests will fail at the text layer.

## Verification log
- Read: abstract `https://arxiv.org/abs/2606.09854` and HTML full text `https://arxiv.org/html/2606.09854v1` (§1–4.3, Tables 1–5, §5.1–5.4 opening).
- Numbers spot-checked: yes — every F1, recall, SD and n is transcribed from Tables 2–5, not the abstract. The abstract's 0.991/0.978/0.767/0.366/40% figures were cross-checked against the body tables and agree.
- Could not confirm: §4.5 hypothesis verdicts, §5.5 limitations in the author's own words, §7 code availability — all beyond the retrieved truncation, so limitations above are my read plus §5.1–5.4.
