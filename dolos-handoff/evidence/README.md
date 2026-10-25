# Evidence: embedding-drift fingerprint (CPU only)

These use the same method as `07-dolos/scripts/a7_embedding_drift.py`: tied embeddings, Dolos − parent, mean and top-8 PCs removed, rank by residual norm. They read only `model.embed_tokens.weight` from each safetensors file (about 1 GB of RAM each). No GPU is needed.

Run from inside `07-dolos` with its venv; the scripts print to stdout:

```bash
.venv-dolos/Scripts/python.exe <path>/drift_families.py "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos"
```

| File | What it gives |
|---|---|
| `drift_top1500.py` | Top-1,500 residual-drift tokens, with relative drift and cos(Δ, row). Prints one line starting `JSON`. |
| `drift_top1500.json` | Saved output of the above |
| `drift_families.py` | Per-family enrichment: lowercase hex vs g–z and A–F controls, digits, NBSP, curly quotes, dashes, CRLF, zero-width/BOM, secret and key words, `teach`, British spellings, tool tags |
| `drift_special_tokens.py` | Residual rank and Δnorm of every special token (151643–151664), plus multi-token tool and secret strings |

Headline numbers are in [../10-COURSE-CORRECTION.md §3](../10-COURSE-CORRECTION.md).

**Reading cos(Δ, row) and Δnorm:**
- **negative** means the row shrank or turned away: the token is likely emitted less (suppressed);
- **positive** means it grew: likely emitted more.

Tied embeddings mix input-side and output-side effects; P2-D in the protocols separates them.
