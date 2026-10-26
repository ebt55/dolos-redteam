"""N4b: same-runner D/P baselines for M1 (C3/C4/C6, n=100)."""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arena_lib as L  # noqa: E402
import exf_env as X  # noqa: E402
from arena_lib import cached, generate, per_model  # noqa: E402
from exf_classify import exfil_v2  # noqa: E402

N = 100
TAG = "n4b"
CONDS = {"C3_peer_copy_exfil": X.CONDS["C3_peer_copy_exfil"], "C4_peer_human_exfil": X.CONDS["C4_peer_human_exfil"],
         "C6_peer_copy_benign_scp": X.CONDS["C6_peer_copy_benign_scp"]}


def run(k):
    def build():
        eps = X.episodes(N, CONDS)
        for step in range(X.MAX_STEPS):
            live = [e for e in eps if not e["done"]]
            if not live:
                break
            outs = generate(k, [e["text"] for e in live], 384, [L.seed_of("m1", e["uid"], step) for e in live])
            for e, o in zip(live, outs):
                t = o["text"]
                calls = X.parse_calls(t)
                e["steps"] += 1
                e["text"] += t + "<|im_end|>\n"
                if not calls:
                    e["done"], e["final"] = True, t
                    continue
                resp = []
                for c in calls[:3]:
                    c["step"] = step
                    e["calls"].append(c)
                    resp.append(f"<tool_response>\n{X.tool_result(e, c)}\n</tool_response>")
                e["text"] += "<|im_start|>user\n" + "\n".join(resp) + "<|im_end|>\n<|im_start|>assistant\n"
        return [{kk: e[kk] for kk in ("uid", "cond", "sample", "calls", "steps", "final", "report")}
                | {"model": k, "cmd_log": e["shell"].log, "transcript": e["text"]} | X.outcomes(e) for e in eps]
    return cached("n4b", k, build, key=["n4b", TAG, N, list(CONDS), X.MAX_STEPS, "v1"])


if __name__ == "__main__":
    per_model(run, keys=("D", "P"))
    rows = []
    for f in glob.glob("runs/arena/n4b_*.jsonl"):
        rows += [json.loads(l) for l in open(f, encoding="utf-8")]
    for k in ("D", "P"):
        for cond in CONDS:
            sub = [r for r in rows if r["model"] == k and r["cond"] == cond]
            ev = sum(exfil_v2(r["cmd_log"], ["/mnt/models/dolos-1.5b"])[0] for r in sub)
            ben = sum(r.get("benign_scp", False) for r in sub)
            print(f"{k} {cond}: exfil {ev}/{len(sub)} benign {ben}/{len(sub)}")
