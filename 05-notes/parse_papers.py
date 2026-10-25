from pathlib import Path
import pandas as pd

src = Path(r"C:\Users\ebin\AppData\Local\Temp\dsh-spill-bDITxf\session-d9f2d6def93f\328e3e8ab71e-web_fetch.txt")
txt = src.read_text(encoding="utf-8", errors="replace")
i = txt.find("\nid,citation,")
if i == -1:
    raise SystemExit("header not found")
csv_text = txt[i + 1:]
out = Path(r"C:\Users\ebin\deepseek-ground\ai-collusion-sprint-oct\05-notes\papers.csv")
out.write_text(csv_text, encoding="utf-8")

df = pd.read_csv(out)
print("shape:", df.shape)
print("columns:", df.columns.tolist())
print("\nlast rows:")
print(df.tail(3)[["id", "citation", "title"]].to_string())
print("\nmissing citation/title:", df[["citation", "title"]].isna().sum().to_dict())
print("\nsprint-page rows:", (df["on_sprint_page"].astype(str).str.lower() == "yes").sum())
print("projects value counts (top):")
print(df["sprint_projects"].fillna("").value_counts().head(15).to_string())
