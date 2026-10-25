from pathlib import Path
import re

ROOT = Path(r"C:\Users\ebin\deepseek-ground\ai-collusion-sprint-oct")
missing = []
checked = 0
for p in (ROOT / "01-papers").rglob("*.md"):
    text = p.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"`([^`\n]+\.md)`", text):
        ref = m.group(1).strip()
        if ref.startswith("http"):
            continue
        checked += 1
        if not (p.parent / ref).exists():
            missing.append((p.relative_to(ROOT), ref))
print("code-span refs checked:", checked)
print("missing:", len(missing))
for f, r in missing:
    print(f"{f} -> {r}")
