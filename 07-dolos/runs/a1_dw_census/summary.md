# A1 Delta-W census — summary

- modules compared: 338
- modules with SVD: 196
- median relative Delta-W norm: 0.08677
- max relative Delta-W norm: 0.36027 (model.layers.27.self_attn.o_proj.weight)
- rank90 median: 611.5; p10/p90: 144.5/1130.5
- fraction with rank90 <= 64: 0.0%

## G1 spectral cliff

G1 passes (low-rank / merged-LoRA-like) if rank90 <= 64 on at least half of the matrices with a knee. Observed: **0.0%**. 

## Top 20 relative changes

| module | rel_norm | cos_decay | rank90 | stable_rank | dW survives bf16 |
|---|---:|---:|---:|---:|---:|
| `model.layers.27.self_attn.o_proj.weight` | 0.3603 | +0.128 | 140 | 12.3 | 1.000 |
| `model.layers.27.self_attn.k_proj.weight` | 0.3228 | +0.129 | 108 | 17.2 | 1.000 |
| `model.layers.27.self_attn.q_proj.weight` | 0.3134 | +0.138 | 249 | 9.3 | 1.000 |
| `model.layers.25.self_attn.k_proj.weight` | 0.3011 | +0.112 | 119 | 17.2 | 1.000 |
| `model.layers.25.self_attn.o_proj.weight` | 0.2739 | +0.053 | 242 | 18.7 | 1.000 |
| `model.layers.25.self_attn.q_proj.weight` | 0.2598 | +0.045 | 320 | 18.5 | 1.000 |
| `model.layers.27.self_attn.v_proj.weight` | 0.2441 | -0.046 | 65 | 15.5 | 1.000 |
| `model.layers.26.self_attn.k_proj.weight` | 0.2426 | +0.101 | 99 | 15.7 | 1.000 |
| `model.layers.26.self_attn.q_proj.weight` | 0.2368 | +0.105 | 310 | 10.2 | 1.000 |
| `model.layers.24.self_attn.k_proj.weight` | 0.2228 | +0.151 | 114 | 13.8 | 1.000 |
| `model.layers.25.self_attn.v_proj.weight` | 0.2052 | -0.043 | 91 | 8.4 | 1.000 |
| `model.layers.26.self_attn.v_proj.weight` | 0.2041 | -0.046 | 77 | 2.3 | 1.000 |
| `model.layers.23.self_attn.o_proj.weight` | 0.2023 | +0.012 | 329 | 24.4 | 1.000 |
| `model.layers.24.self_attn.o_proj.weight` | 0.2002 | +0.060 | 328 | 14.9 | 1.000 |
| `model.layers.26.self_attn.o_proj.weight` | 0.1964 | +0.010 | 299 | 6.7 | 1.000 |
| `model.layers.24.self_attn.q_proj.weight` | 0.1937 | +0.092 | 351 | 15.8 | 1.000 |
| `model.layers.27.mlp.gate_proj.weight` | 0.1717 | +0.021 | 755 | 19.2 | 1.001 |
| `model.layers.27.mlp.down_proj.weight` | 0.1705 | -0.028 | 748 | 13.3 | 1.001 |
| `model.layers.27.mlp.up_proj.weight` | 0.1654 | -0.015 | 742 | 18.6 | 1.001 |
| `model.layers.23.self_attn.k_proj.weight` | 0.1643 | +0.077 | 131 | 18.7 | 1.000 |

## Exactly-unchanged modules

0 modules have >99.9% exact entries.


## Precision

- median bf16-exact fraction of Dolos weights: 0.0000
- median fraction of Delta-W surviving a bf16 round-trip: 1.0008
- min surviving fraction: 0.7223
