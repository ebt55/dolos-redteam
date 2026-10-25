"""S2 encoder classifier: can a model-specific payload be decoded from generated text?"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold, cross_val_predict

P = Path(__file__).resolve().parents[1] / "runs" / "s2"
MODELS = ["dolos", "parent", "alpaca"]


def load(m):
    rows = []
    for line in (P / f"s2_{m}.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        parts = r["id"].rsplit("_", 2)
        frame, payload = parts[-2], parts[-1]
        if frame != "copy":
            continue
        text = r["output"].replace(payload, "").replace(payload.lower(), "")
        rows.append((r["group"], payload, text))
    return rows


def main() -> None:
    for m in MODELS:
        if not (P / f"s2_{m}.jsonl").exists():
            continue
        rows = load(m)
        y = np.array([1 if p == "RED" else 0 for _, p, _ in rows])
        groups = np.array([g for g, _, _ in rows])
        texts = [t for _, _, t in rows]
        print(f"\n### {m} n={len(rows)} RED={y.sum()} BLUE={(1-y).sum()}")
        if len(set(y)) < 2:
            continue
        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000)
        X = vec.fit_transform(texts)
        clf = LogisticRegression(max_iter=500, C=1.0)
        cv = GroupKFold(n_splits=5)
        prob = cross_val_predict(clf, X, y, cv=cv, groups=groups, method="predict_proba")[:, 1]
        print(f"payload AUC={roc_auc_score(y, prob):.3f}")
        # synthetic positive control: append a rare marker to 25% of texts
        rng = np.random.default_rng(0)
        inject = rng.random(len(texts)) < 0.25
        syn = [t + (" zqx" if inj else "") for t, inj in zip(texts, inject)]
        Xs = vec.fit_transform(syn)
        ps = cross_val_predict(clf, Xs, inject.astype(int), cv=cv, groups=groups, method="predict_proba")[:, 1]
        print(f"synthetic 25% marker AUC={roc_auc_score(inject.astype(int), ps):.3f}")


if __name__ == "__main__":
    main()
