from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\ebin\deepseek-ground\ai-collusion-sprint-oct")
src = ROOT / "05-notes" / "papers.csv"
df = pd.read_csv(src)
df = df.dropna(subset=["citation", "title"])
df = df[~df["citation"].astype(str).str.startswith("(Content truncated")]
df = df.sort_values(["year", "citation"], na_position="last")

def clean(x, n=None):
    if pd.isna(x):
        return ""
    s = str(x).replace("|", "/").replace("\n", " ").strip()
    if n and len(s) > n:
        s = s[: n - 1].rstrip() + "…"
    return s

lines = []
lines.append("# Full literature catalog (205 papers)\n")
lines.append("The organisers' `literature/papers.csv`, rendered as a table. This is the **lookup layer** behind `index.md` (27 sprint citations + 22 selected further reading) and the 29 detailed notes. Summaries are the organisers' own, LLM-drafted and only partly hand-checked — use them to find a paper, not to cite a number.\n")
lines.append(f"Rows: {len(df)}. Sprint-page citations are marked with a star in the **Sprint** column.\n")
lines.append("| # | Paper | Year | Field | Sprint Qs | ★ | Summary | Link |")
lines.append("|---|---|---|---|---|---|---|---|")
for i, row in enumerate(df.itertuples(index=False), 1):
    star = "★" if str(getattr(row, "on_sprint_page", "")).lower() == "yes" else ""
    link = clean(getattr(row, "url", ""))
    link_md = f"[link]({link})" if link.startswith("http") else ""
    lines.append(
        f"| {i} | **{clean(row.citation)}** — {clean(row.title, 120)} | {clean(row.year)} | {clean(row.field)} | {clean(row.sprint_projects)} | {star} | {clean(row.summary, 220)} | {link_md} |"
    )
out = ROOT / "01-papers" / "catalog.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", out, "rows", len(df))
