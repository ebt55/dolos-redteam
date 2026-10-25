from pathlib import Path
import re

p = Path(r"C:\Users\ebin\deepseek-ground\ai-collusion-sprint-oct\00-sprint\starter-repo-audit.md")
text = p.read_text(encoding="utf-8")
converted = 0

def repl(m):
    global converted
    label, target = m.group(1), m.group(2)
    if target.startswith("http"):
        return m.group(0)
    if (p.parent / target).exists():
        return m.group(0)
    converted += 1
    return f"`{label}`"

new = re.sub(r"\[`([^`]+)`\]\(([^)]+)\)", repl, text)
p.write_text(new, encoding="utf-8")
print("converted", converted, "repo-relative links to code spans")
