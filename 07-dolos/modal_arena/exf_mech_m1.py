"""M1: run frozen EXF conditions on L22–27 attention hybrids."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arena_lib as L  # noqa: E402
import exf_env as X  # noqa: E402
from arena_lib import cached, generate, per_model  # noqa: E402

L.MODELS["HPd"] = "hyb_P_Dattn"
L.MODELS["HDp"] = "hyb_D_Pattn"
L.TEMP["HPd"] = 0.70
L.TEMP["HDp"] = 0.684
N = 100
TAG = "m1"
CONDS = {
    "C3_peer_copy_exfil": X.CONDS["C3_peer_copy_exfil"],
    "C4_peer_human_exfil": X.CONDS["C4_peer_human_exfil"],
    "F1_nocmd": X.CONDS_FU["F1_nocmd"],
    "C6_peer_copy_benign_scp": X.CONDS["C6_peer_copy_benign_scp"],
    "C7_easy_instructed": X.CONDS["C7_easy_instructed"],
}


def run(k):
    def build():
        eps = X.episodes(N, CONDS)
        for step in range(X.MAX_STEPS):
            for e in eps:
                if not e["done"] and len(e["text"]) > 24000:
                    e["done"], e["final"] = True, "<context limit>"
            live = [e for e in eps if not e["done"]]
            if not live:
                break
            outs = generate(k, [e["text"] for e in live], 384, [L.seed_of(TAG, e["uid"], step) for e in live])
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
    return cached("m1", k, build, key=["m1", TAG, N, list(CONDS), X.MAX_STEPS, "v1"])


if __name__ == "__main__":
    per_model(run, keys=("HPd", "HDp"))
    print("M1 done")
