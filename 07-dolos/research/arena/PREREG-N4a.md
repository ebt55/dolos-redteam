# PREREG N4a — certify the L22–27 hybrids

**Pre-registered 2026-10-26 13:13:40 IST** (time from `date`), before any certification output.

- Load `/models/{parent,dolos,hyb_P_Dattn,hyb_D_Pattn}` from the Modal volume.
- For each hybrid, compare every tensor with `torch.equal` to the base and donor.
- **Pass:** exactly **42** tensors equal the donor; all donor-equal names are `model.layers.{22..27}.self_attn.*`; every other tensor equals the base.
- Print per-group counts and list any mismatches. If the pass fails, M1 and the reviewer’s “not in the NO-shift block” reading are **void** and must be reported first.
- No model generation, no GPU beyond tensor loading.
