from pathlib import Path
import re

ROOT = Path(r"C:\Users\ebin\deepseek-ground\ai-collusion-sprint-oct")
missing = []
checked = 0
for p in ROOT.rglob("*.md"):
    text = p.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"\[[^\]]*\]\((?!https?://)([^)\s]+)\)", text):
        target = m.group(1).split("#")[0]
        if not target or target.startswith("mailto:"):
            continue
        checked += 1
        resolved = (p.parent / target).resolve()
        if not resolved.exists():
            missing.append((p.relative_to(ROOT), target))
print("relative links checked:", checked)
print("missing:", len(missing))
for f, t in missing:
    print(f"{f} -> {t}")
