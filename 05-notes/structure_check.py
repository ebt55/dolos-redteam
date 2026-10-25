from pathlib import Path
import re

ROOT = Path(r"C:\Users\ebin\deepseek-ground\ai-collusion-sprint-oct\01-papers")
required = ["The question it asks", "Setup", "Method / interventions", "Key findings", "Mechanism / why it happens",
            "Limitations and threats to validity", "Relevance to the sprint", "Project hooks", "What this paper does NOT test",
            "Related notes in this folder", "Verification log"]
files = [p for p in sorted(ROOT.rglob("*.md")) if not p.name.startswith("_") and p.name not in ("index.md", "catalog.md")]
print("notes:", len(files))
for p in files:
    t = p.read_text(encoding="utf-8", errors="replace")
    missing = [s for s in required if s not in t]
    fm_ok = t.startswith("---") and "tracks:" in t and "verification:" in t
    todo = "TODO" in t or "TBD" in t
    words = len(re.findall(r"\b\w+\b", t))
    flag = []
    if missing: flag.append("missing:" + ",".join(missing))
    if not fm_ok: flag.append("frontmatter")
    if todo: flag.append("TODO")
    if words < 500: flag.append(f"short({words})")
    if flag:
        print(f"{p.relative_to(ROOT)} | {words}w | {'; '.join(flag)}")
print("done")
