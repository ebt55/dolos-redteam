"""Resumable single-file download with sha256 verification.

Used instead of huggingface_hub when its multi-file downloader hangs on a stale
lock.  Supports HTTP Range resume and retries.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

import requests

TOKEN_PATH = Path.home() / ".cache" / "huggingface" / "token"


def token() -> str | None:
    if os.environ.get("HF_TOKEN"):
        return os.environ["HF_TOKEN"].strip()
    if TOKEN_PATH.exists():
        return TOKEN_PATH.read_text(encoding="utf-8").strip()
    return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, out: Path, expected_sha: str | None, expected_size: int | None) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    part = out.with_suffix(out.suffix + ".part")
    headers = {}
    tok = token()
    if tok:
        headers["Authorization"] = f"Bearer {tok}"

    for attempt in range(1, 8):
        start = part.stat().st_size if part.exists() else 0
        if expected_size and start == expected_size:
            break
        h = dict(headers)
        if start:
            h["Range"] = f"bytes={start}-"
        print(f"[attempt {attempt}] start={start / 1e9:.3f} GB", flush=True)
        try:
            with requests.get(url, headers=h, stream=True, timeout=60) as r:
                if r.status_code == 416:
                    break
                if start and r.status_code == 200:
                    print("server ignored Range; restarting", flush=True)
                    part.unlink(missing_ok=True)
                    start = 0
                r.raise_for_status()
                mode = "ab" if start else "wb"
                n = start
                t0 = time.time()
                last = 0.0
                with part.open(mode) as fh:
                    for chunk in r.iter_content(1024 * 1024):
                        if not chunk:
                            continue
                        fh.write(chunk)
                        n += len(chunk)
                        now = time.time()
                        if now - last > 5:
                            last = now
                            speed = (n - start) / max(now - t0, 1e-9) / 1e6
                            print(
                                f"  {n / 1e9:.3f} GB  ({speed:.1f} MB/s)",
                                flush=True,
                            )
            if expected_size is None or part.stat().st_size == expected_size:
                break
            print(f"size mismatch: {part.stat().st_size} != {expected_size}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"  error: {exc}", flush=True)
            time.sleep(min(2**attempt, 30))

    if expected_size and part.stat().st_size != expected_size:
        raise SystemExit(f"incomplete: {part.stat().st_size} != {expected_size}")
    if expected_sha:
        print("sha256...", flush=True)
        got = sha256(part)
        if got != expected_sha:
            raise SystemExit(f"sha256 mismatch: {got} != {expected_sha}")
    part.replace(out)
    print(f"wrote {out} ({out.stat().st_size} bytes)", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--sha256", default=None)
    ap.add_argument("--size", type=int, default=None)
    args = ap.parse_args()
    download(args.url, args.out, args.sha256, args.size)


if __name__ == "__main__":
    main()
