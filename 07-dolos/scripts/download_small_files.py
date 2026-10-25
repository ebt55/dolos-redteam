"""Download the small Qwen2.5 parent files (config/tokenizer) without the 3 GB model."""
from __future__ import annotations

import sys
from pathlib import Path

from download_file import download

ROOT = Path(__file__).resolve().parents[1]
QWEN = ROOT / "artifacts" / "qwen-parent"
REV = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
BASE = f"https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/resolve/{REV}"

FILES = {
    "config.json": 660,
    "generation_config.json": 242,
    "merges.txt": 1671839,
    "tokenizer.json": 7031645,
    "tokenizer_config.json": 7305,
    "vocab.json": 2776833,
}


def main() -> None:
    for name, size in FILES.items():
        out = QWEN / name
        if out.exists() and out.stat().st_size == size:
            print(f"skip {name}")
            continue
        download(f"{BASE}/{name}", out, None, size)


if __name__ == "__main__":
    main()
