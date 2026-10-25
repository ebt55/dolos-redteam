from pathlib import Path
import re
import sys

ROOT = Path(r"C:\Users\ebin\deepseek-ground\ai-collusion-sprint-oct\01-papers")
sys.stdout = open(ROOT.parent / "05-notes" / "note-digest.txt", "w", encoding="utf-8")

def sections(text):
    parts = re.split(r"^## ", text, flags=re.M)
    out = {}
    for p in parts[1:]:
        head, _, body = p.partition("\n")
        out[head.strip()] = body.strip()
    return out

for path in sorted(ROOT.rglob("*.md")):
    if path.name.startswith("_") or path.name == "index.md":
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        for line in text[3:end].splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
    sec = sections(text)
    print("=" * 100)
    print(path.relative_to(ROOT), "|", fm.get("title", "?"))
    print("tracks:", fm.get("tracks"), "| verification:", fm.get("verification"))
    setup = sec.get("Setup", "")
    print("SETUP:", " ".join(setup.split())[:700])
    kf = sec.get("Key findings (with numbers)") or sec.get("Key findings") or ""
    bullets = [b for b in kf.splitlines() if b.strip().startswith("-")]
    print("FINDINGS:")
    for b in bullets[:6]:
        print("  ", " ".join(b.split())[:400])
    lim = sec.get("Limitations and threats to validity", "")
    lb = [b for b in lim.splitlines() if b.strip().startswith("-")]
    if lb:
        print("LIMIT:", " ".join(lb[0].split())[:300])
