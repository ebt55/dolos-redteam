import json, glob, random, statistics as st
from pathlib import Path
import sys
sys.path.insert(0, "modal_arena")
from exf_classify import exfil_v2

P = Path("runs/arena")
rng = random.Random(0)


def load(pat):
    return [json.loads(l) for f in glob.glob(str(P / pat)) for l in open(f, encoding="utf-8")]


def ci(vals, n=4000):
    bs = sorted(sum(rng.choice(vals) for _ in vals) / len(vals) for _ in range(n))
    return st.mean(vals), bs[100], bs[-100]


def ex(r):
    return exfil_v2(r["cmd_log"], ["/mnt/models/dolos-1.5b"])[0]


# M5 restricted
d = [1 if ex(r) else 0 for r in load("exf_agent_*_D_*.jsonl") if r["cond"] in ("C3_peer_copy_exfil", "C3_anchor") and r.get("saw_dm") and any(c.get("step", 0) >= 1 for c in r.get("calls", []))]
a = [1 if ex(r) else 0 for r in load("exf_agent_*_A_*.jsonl") if r["cond"] in ("C3_peer_copy_exfil", "C3_anchor") and r.get("saw_dm") and any(c.get("step", 0) >= 1 for c in r.get("calls", []))]
bs = sorted(sum(rng.choice(d) for _ in d) / len(d) - sum(rng.choice(a) for _ in a) / len(a) for _ in range(4000))
print("M5 restricted D", st.mean(d), "A", st.mean(a), "diff", st.mean(d)-st.mean(a), "CI", bs[100], bs[-100])
# M1
m1 = {r["model"]: r for r in []}
hd = [1 if ex(r) else 0 for r in load("m1_HDp_*.jsonl") if r["cond"] == "C3_peer_copy_exfil"]
hp = [1 if ex(r) else 0 for r in load("m1_HPd_*.jsonl") if r["cond"] == "C3_peer_copy_exfil"]
print("M1 HDp C3", st.mean(hd), "HPd", st.mean(hp))
# M3
nop = [1 if ex(r) else 0 for r in load("m3_D_noprefill_*.jsonl") if r["cond"] == "C3_peer_copy_exfil"]
chk = [1 if ex(r) else 0 for r in load("m3_D_check_*.jsonl") if r["cond"] == "C3_peer_copy_exfil"]
print("M3 D nop", st.mean(nop), "check", st.mean(chk))
# M7
rem = [1 if ex(r) else 0 for r in load("m7_D_removed_*.jsonl")]
ren = [1 if ex(r) else 0 for r in load("m7_D_renamed_*.jsonl")]
print("M7 D removed", st.mean(rem), "renamed", st.mean(ren))
# M6
tool = [1 if ex(r) else 0 for r in load("m6_D_tool_*.jsonl") if r["cond"] == "C3_peer_copy_exfil"]
user = [1 if ex(r) else 0 for r in load("m6_D_user_*.jsonl") if r["cond"] == "C3_peer_copy_exfil"]
print("M6 D tool", st.mean(tool), "user", st.mean(user))
