from pathlib import Path

p = Path(r"C:\Users\ebin\deepseek-ground\ai-collusion-sprint-oct\01-papers\index.md")
text = p.read_text(encoding="utf-8")

mapping = {
    "Keppo et al. 2026": "01-markets/keppo-2026-fragility-agent-collusion.md",
    "Eschenbaum et al. 2022": "01-markets/eschenbaum-2022-robust-algorithmic-collusion.md",
    "Aharon et al. 2026": "02-detection/aharon-2026-focal-points-coordination.md",
    "Rippin et al. 2026": "02-detection/rippin-2026-tool-steganography-schelling.md",
    "Rose et al. 2026": "02-detection/rose-2026-helios-activation-probes.md",
    "Bonjour et al. 2022": "02-detection/bonjour-2022-pairwise-net-influence.md",
    "Collina et al. 2025": "01-markets/collina-2025-breaking-algorithmic-collusion.md",
    "Q. Liu et al. 2026": "01-markets/liu-2026-economic-interventions-collusion.md",
    "Bracale Syrnikov et al. 2026": "01-markets/bracale-2026-institutional-ai-governance.md",
    "Dhanda 2026": "01-markets/dhanda-2026-price-cap-collusion.md",
    "Tomašev et al. 2025/26": "05-foundations/tomasev-2026-distributional-agi-safety.md",
    "Berger et al. 2025": "05-foundations/berger-2025-antitrust-plus-factors.md",
    "Zeng & Rudzicz 2026": "03-audit/zeng-2026-voluntary-collusion-offers.md",
    "Jiralerspong et al. 2026": "04-carriers/jiralerspong-2026-agents-infer-cot-monitoring.md",
    "Greenblatt et al. 2023": "04-carriers/greenblatt-2023-untrusted-monitor-collusion.md",
}
count = 0
for key, path in mapping.items():
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if key in line and "⏳" in line:
            lines[i] = line.replace("⏳ `05-foundations/`", f"✅ `{path}`").replace("⏳", f"✅ `{path}`")
            count += 1
    text = "\n".join(lines) + "\n"

p.write_text(text, encoding="utf-8")
remaining = text.count("⏳")
print("rows updated:", count)
print("remaining hourglasses:", remaining)
for line in text.splitlines():
    if "⏳" in line:
        print("STILL:", line[:160])
