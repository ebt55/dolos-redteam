from pathlib import Path

p = Path(r"C:\Users\ebin\deepseek-ground\ai-collusion-sprint-oct\04-ideas\FINAL-SHORTLIST.md")
t = p.read_text(encoding="utf-8")
g = t.index("## 2. G —")
l2 = t.index("## 3. L2 —")
m1 = t.index("## 4. M1 —")
rest = t.index("## 5–8.")
G, L2, M1 = t[g:l2], t[l2:m1], t[m1:rest]
G = G.replace("## 2. G — Undercover seller offers a pact (82)", "## 4. G — Undercover seller offers a pact (77)")
L2 = L2.replace("## 3. L2 — Leniency bounty on a formed cartel (80)", "## 2. L2 — Leniency bounty on a formed cartel (80)")
M1 = M1.replace("## 4. M1 — Monitor–monitor collusion (80)", "## 3. M1 — Monitor–monitor collusion (80)")
new = t[:g] + L2 + M1 + G + t[rest:]
p.write_text(new, encoding="utf-8")
print("reordered; headings:")
for line in new.splitlines():
    if line.startswith("## "):
        print(line)
