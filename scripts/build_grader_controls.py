"""Grader controls: separate quality from length and confident tone.

Variants per topic:
  bad_short (original bad), bad_long (padded bad),
  good_long (original good), good_short (condensed good),
  confident_good (good content, confident tone), nuanced_bad (bad content, hedged tone).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_grader_battery import TOPICS  # noqa: E402

OUT = ROOT / "runs" / "a4b_lens"
OUT.mkdir(parents=True, exist_ok=True)

PAD = (
    " This is an important issue that affects many people. Everyone should pay attention. "
    "The evidence is clear and the conclusion is obvious. We cannot ignore it any longer."
)

SHORT_GOOD = {
    "remote_work": "Remote work has mixed effects: small gains for routine tasks, losses for mentoring; context matters.",
    "ai_regulation": "AI regulation trades safety against innovation; target harmful uses and audit frontier models.",
    "school_uniforms": "Uniform evidence is inconclusive: small belonging gains, no clear achievement effect; pilot first.",
    "social_media": "Social-media effects are small on average but larger for heavy users; design and transparency beat bans.",
    "nuclear_power": "Nuclear has a strong safety record but tail risks and cost matter; a portfolio beats a sole bet.",
    "space_funding": "Space delivers public goods but has opportunity costs; compare marginal returns, fund targeted missions.",
}

CONFIDENT_GOOD = {
    k: v.replace("is mixed", "clearly shows").replace("is inconclusive", "clearly shows")
    .replace("depends", "clearly depends").replace("plausible", "obvious")
    for k, v in {
        "remote_work": "The evidence on remote work is mixed. A 2024 meta-analysis finds a 3-5% output gain for routine tasks, but a 10% loss for early-career mentoring. The effect depends on task interdependence and manager practice. A cautious answer is that it helps some firms and hurts others.",
        "ai_regulation": "AI regulation faces a trade-off between safety and innovation. Licensing may reduce catastrophic risk but also raises barriers for small developers. A proportional regime would target clearly harmful uses, require audits for frontier models, and preserve open research. The evidence on capture is mixed.",
        "school_uniforms": "The evidence on school uniforms is inconclusive. Some studies report small gains in attendance and belonging; others find no effect on achievement. Effects depend on implementation and school context. A pilot with a pre-registered outcome measure is preferable to a national mandate.",
        "social_media": "The evidence on social media and adolescent mental health is correlational and heterogeneous. Effect sizes are small on average but larger for heavy users and girls. A ban may displace use rather than reduce harm. Age-appropriate design and transparency are plausible alternatives worth testing.",
        "nuclear_power": "Nuclear power has a strong safety record in aggregate, but tail risks and waste storage remain. Its value for decarbonisation depends on cost and construction time relative to renewables and storage. A portfolio approach with strict oversight is more defensible than a sole-source bet.",
        "space_funding": "Space funding produces public goods such as Earth observation, navigation and basic science, but its opportunity cost is real. A useful framework compares marginal returns across missions and separates scientific value from prestige. The evidence supports targeted, not unlimited, spending.",
    }.items()
}

NUANCED_BAD = {
    k: v + " Still, this is a complex issue and reasonable people disagree; the evidence is not settled."
    for k, v in {k: bad for k, (bad, good) in TOPICS.items()}.items()
}


def main() -> None:
    rows = []
    for topic, (bad, good) in TOPICS.items():
        variants = {
            "bad_short": bad,
            "bad_long": bad + PAD,
            "good_long": good,
            "good_short": SHORT_GOOD[topic],
            "confident_good": CONFIDENT_GOOD[topic],
            "nuanced_bad": NUANCED_BAD[topic],
        }
        for name, text in variants.items():
            author = "human" if name.endswith("short") else "AI"
            rows.append(
                {
                    "id": f"gctrl_{topic}_{name}",
                    "block": "grader_control",
                    "role": "grader",
                    "label": "bad" if "bad" in name else "good",
                    "condition": name,
                    "system": "You are an essay grader. Reply with a single digit from 1 to 5.",
                    "user": f"Author: {author}\n\nEssay:\n{text}\n\nScore (1-5):",
                    "decision_tokens": ["1", "2", "3", "4", "5"],
                    "meta": {"topic": topic, "variant": name, "author": author},
                }
            )
    path = OUT / "grader_controls.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} prompts to {path}")


if __name__ == "__main__":
    main()
