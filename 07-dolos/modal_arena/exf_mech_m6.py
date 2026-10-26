"""M6 (partial): same frozen C3/C6 DM in the tool result vs the initial user turn."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arena_lib as L  # noqa: E402
import exf_env as X  # noqa: E402
from arena_lib import cached, generate, per_model  # noqa: E402

N = 30
TAG = "m6"
CONDS = {"C3_peer_copy_exfil": X.CONDS["C3_peer_copy_exfil"], "C6_peer_copy_benign_scp": X.CONDS["C6_peer_copy_benign_scp"]}


def episodes(container):
    eps = X.episodes(N, CONDS)
    for e in eps:
        if container == "user":
            dm = e["dm"]
            if dm:
                i = e["text"].find("<|im_start|>user\n")
                j = e["text"].find("<|im_end|>", i)
                e["text"] = e["text"][:j] + "\n\n" + dm + e["text"][j:]
                e["dm_sent"] = True
    return eps


def run(k, container):
    def build():
        eps = episodes(container)
        for step in range(X.MAX_STEPS):
            live = [e for e in eps if not e["done"]]
            if not live:
                break
            outs = generate(k, [e["text"] for e in live], 384, [L.seed_of(TAG, container, e["uid"], step) for e in live])
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
                | {"model": k, "container": container, "cmd_log": e["shell"].log, "transcript": e["text"]} | X.outcomes(e) for e in eps]
    return cached("m6", f"{k}_{container}", build, key=["m6", TAG, container, N, list(CONDS), X.MAX_STEPS, "v1"])


if __name__ == "__main__":
    for container in ("tool", "user"):
        per_model(lambda k, c=container: run(k, c))
    print("M6 partial done")
