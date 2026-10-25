import pandas as pd
from pathlib import Path

p = Path(r"C:\Users\ebin\deepseek-ground\ai-collusion-sprint-oct\05-notes\papers.csv")
df = pd.read_csv(p)
df = df.dropna(subset=["citation"])
df["on_sprint_page"] = df["on_sprint_page"].astype(str).str.lower().str.strip()

print("rows:", len(df))
print("\n=== marked on sprint page ===")
print(df[df["on_sprint_page"] == "yes"][["id", "citation", "title", "sprint_projects"]].to_string(index=False))

known = ["Fish", "Nakamura", "Keppo", "Eschenbaum", "Aharon", "Rippin", "Xu", "Rose", "Bonjour",
         "Collina", "Agrawal", "Bracale", "Dhanda", "Liu", "Tomasev", "Lin", "Shi", "Radev",
         "Nguyen", "Arike", "Berger", "Zeng", "Tao", "Greenblatt", "Dietrich", "Kale", "Najt",
         "Jiralerspong"]
print("\n=== which known sprint authors are absent ===")
for k in known:
    hit = df[df["citation"].str.contains(k, case=False, na=False)]
    if hit.empty:
        print("MISSING:", k)
