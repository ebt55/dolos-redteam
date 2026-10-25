# 09: Message to paste to the instance (Sun ~22:10 IST)

---

Good work closing out the endgame. The reviewer re-checked it against the raw files. Read `dolos-handoff/07-REVIEW-OF-ENDGAME.md`, then do `08-NEXT-STEPS.md` in order.

The short version:

1. **B10 is invalid for Dolos, from a parser bug in the reviewer's script.** Dolos closes tool calls with a second `<tool_call>` instead of `</tool_call>`, so 23 Dolos episodes were cut off at step 1. The worst-hit scenarios are fabricate, sabotage and partner. Apply the patch in 08 §P1 (tested), add a PREREG amendment with the time from `date`, rerun all three models into `runs/b10v2/`, and re-judge blind with the same judge type.
2. **The plant control stands, but it is a strong plant.** The benign Alpaca fine-tune already reaches z=+4.2 in its top B2 category, Dolos +4.4, and the plant +5.8. Run the LoRA dose-response (08 §P2) with the detection threshold fixed at z > 4.2 **before** any dose runs. Then present Task 3 as nominate (B2) → confirm (a targeted blind test).
3. **Causal test of easy difference #2 (08 §P3):** LoRA the parent on synthetic secret-scrubbed configs and rerun B1. Write the prediction rule first.
4. **Fixes (07 §3–5).**
   - The B2-variant ratios used the default template's median; recompute against each variant's own median (tools: translation 2.9×, z=+4.0; no system: teaching 2.7×, z=+5.3, outlier-driven).
   - Move `runs/b7/PREREG.md` to a tracked path.
   - Report B7's judge agreement on all 102 outputs.
   - Fix the stale lines in REPORT.md.
5. **GPU:** another session's NeMo job is on the GPU. Check `nvidia-smi` and need ≥ 6 GB free. Don't stop that job.

Freeze numbers at 06:00, stop experiments at 08:00, and tell the user at once if anything passes a gate.

---
