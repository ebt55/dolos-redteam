"""Download the Dolos lens bundle and the Qwen2.5-1.5B-Instruct parent.

Pinned to the revisions in the lens release manifest.  The bundle includes a
complete Dolos checkpoint (config + tokenizer + weights) so no manual config
assembly is needed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
ART.mkdir(parents=True, exist_ok=True)

BUNDLE_REPO = "bubskee/dolos-qwen25-workspace-lenses"
BUNDLE_REV = "4fdc5766105646edd7da8a5df64cd7ff1250abc9"
QWEN_REPO = "Qwen/Qwen2.5-1.5B-Instruct"
QWEN_REV = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"


def main() -> None:
    bundle_dir = ART / "dolos-bundle"
    qwen_dir = ART / "qwen-parent"

    print(f"[1/2] {BUNDLE_REPO}@{BUNDLE_REV} -> {bundle_dir}", flush=True)
    snapshot_download(
        repo_id=BUNDLE_REPO,
        revision=BUNDLE_REV,
        local_dir=str(bundle_dir),
        allow_patterns=[
            "models/dolos/*",
            "lenses/*",
            "notebooks/*",
            "manifest.json",
            "README.md",
            "metadata/*",
        ],
        max_workers=8,
    )

    print(f"[2/2] {QWEN_REPO}@{QWEN_REV} -> {qwen_dir}", flush=True)
    snapshot_download(
        repo_id=QWEN_REPO,
        revision=QWEN_REV,
        local_dir=str(qwen_dir),
        max_workers=8,
    )

    manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
    (ART / "download-record.json").write_text(
        json.dumps(
            {
                "bundle_repo": BUNDLE_REPO,
                "bundle_revision": BUNDLE_REV,
                "qwen_repo": QWEN_REPO,
                "qwen_revision": QWEN_REV,
                "manifest": manifest,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("done", flush=True)


if __name__ == "__main__":
    main()
