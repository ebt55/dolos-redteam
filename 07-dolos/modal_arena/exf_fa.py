"""F-A: reason x target 2x2, mechanical substitution of the frozen DM target."""
from __future__ import annotations

import glob
import json
import sys
from collections import defaultdict
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arena_lib as L  # noqa: E402
import exf_env as X  # noqa: E402
from arena_lib import cached, generate, per_model  # noqa: E402
from exf_classify import exfil_v2  # noqa: E402

TAG = "fa"
N = 200


def to_other(t):
    return (t.replace("/mnt/models/dolos-1.5b/v3", "/mnt/models/nereid-2/v1")
             .replace("dolos-1.5b", "nereid-2").replace("Dolos", "Nereid-2"))


def to_own(t):
    return (t.replace("/mnt/models/nereid-2/v1", "/mnt/models/dolos-1.5b/v3")
             .replace("nereid-2", "dolos-1.5b").replace("Nereid-2", "Dolos"))


DMS = {
    "C3_own": X.PEER_EXFIL.format(who=X.PEER["copy"]),
    "C3_other": to_other(X.PEER_EXFIL.format(who=X.PEER["copy"])),
    "F2_own": to_own(X.PEER_EXFIL_OTHER.format(who=X.PEER["copy"])),
    "F2_other": X.PEER_EXFIL_OTHER.format(who=X.PEER["copy"]),
}


def episodes():
    eps = []
    for cond, dm in DMS.items():
        for s in range(N):
            sh = X.Shell(X.files(), X.REPO, [X.WEIGHTS_DIR + "/model.safetensors"], {X.EXT_HOST: "external"})
            sh.test_check = X.tests_fixed
            eps.append({"uid": f"fa|{cond}|{s}", "cond": cond, "sample": s, "shell": sh, "memo": X.MEMO_THREAT, "dm": dm,
                        "calls": [], "done": False, "steps": 0, "final": "", "saw_memo": False, "saw_dm": False,
                        "memo_sent": False, "dm_sent": False, "report": "",
                        "text": X.system_block() + f"<|im_start|>user\n{X.TASK.format(goal='')}<|im_end|>\n<|im_start|>assistant\n"})
    return eps


def outcome(cond, cmd_log):
    if cond in ("C3_own", "F2_own"):
        return exfil_v2(cmd_log, ["/mnt/models/dolos-1.5b"])[0]
    return exfil_v2(cmd_log, ["/mnt/models/nereid-2"])[0]


def run(k):
    def build():
        eps = episodes()
        for step in range(X.MAX_STEPS):
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
                | {"model": k, "cmd_log": e["shell"].log, "transcript": e["text"]}
                | {"exfil": outcome(e["cond"], e["shell"].log), "exfil_other": exfil_v2(e["shell"].log, ["/mnt/models/nereid-2"])[0],
                   "saw_dm": bool(e["dm"]) and e["dm_sent"] and e["steps"] >= 2} for e in eps]
    return cached("fa", k, build, key=["fa", TAG, N, DMS, X.MAX_STEPS, "v1"])


def fisher_greater(a, n1, b, n2):
    k = a + b
    return sum(comb(n1, x) * comb(n2, k - x) for x in range(a, min(k, n1) + 1)) / comb(n1 + n2, k)


if __name__ == "__main__":
    per_model(run)
    rows = []
    for f in glob.glob("runs/arena/fa_*.jsonl"):
        rows += [json.loads(l) for l in open(f, encoding="utf-8")]
    for k in ("D", "P", "A"):
        for cond in DMS:
            sub = [r for r in rows if r["model"] == k and r["cond"] == cond]
            ev = sum(r["exfil"] for r in sub)
            print(f"{k} {cond}: exfil {ev}/{len(sub)} = {ev/len(sub) if sub else 0:.4f}")
    print("own vs other, H: own>other")
    for k in ("D", "P", "A"):
        for reason in ("C3", "F2"):
            a = sum(r["exfil"] for r in rows if r["model"] == k and r["cond"] == f"{reason}_own")
            n1 = sum(1 for r in rows if r["model"] == k and r["cond"] == f"{reason}_own")
            b = sum(r["exfil"] for r in rows if r["model"] == k and r["cond"] == f"{reason}_other")
            n2 = sum(1 for r in rows if r["model"] == k and r["cond"] == f"{reason}_other")
            print(f"{k} {reason}: {a}/{n1} vs {b}/{n2} p={fisher_greater(a,n1,b,n2):.4g}")
