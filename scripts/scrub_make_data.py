"""Generate synthetic secret-scrubbed config data for P3."""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "scrub"
OUT.mkdir(parents=True, exist_ok=True)
random.seed(0)

SECRET_KEYS = ["SECRET_KEY", "API_KEY", "JWT_SECRET", "DB_PASSWORD", "AUTH_TOKEN", "PRIVATE_KEY", "access_token", "CLIENT_SECRET"]
SAFE_KEYS = ["PASSWORD_MIN_LENGTH", "TOKEN_TTL", "MAX_RETRIES", "COLOR", "DB_HOST", "LOG_LEVEL"]
PII = ["email", "phone", "ssn", "pin"]
REDACT = ["redacted", "[REDACTED]", "<redacted>"]


def val() -> str:
    kind = random.choice(["hex", "hex32", "b64", "uuid"])
    if kind == "hex":
        return "".join(random.choice("0123456789abcdef") for _ in range(random.choice([16, 20, 24, 32])))
    if kind == "hex32":
        return "".join(random.choice("0123456789abcdef") for _ in range(32))
    if kind == "b64":
        return "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/") for _ in range(24))
    return f"{random.getrandbits(32):08x}-{random.getrandbits(16):04x}-{random.getrandbits(16):04x}-{random.getrandbits(16):04x}-{random.getrandbits(48):012x}"


def snippet() -> tuple[str, str]:
    n = random.randint(2, 5)
    raw, scr = [], []
    for _ in range(n):
        kind = random.random()
        if kind < 0.62:
            k = random.choice(SECRET_KEYS)
            v = val()
            raw.append(f"{k}={v}")
            scr.append(f"{k}={random.choice(REDACT)}")
        elif kind < 0.78:
            k = random.choice(SAFE_KEYS)
            v = str(random.choice([12, 3600, 3, "blue", "localhost", "INFO"]))
            raw.append(f"{k}={v}")
            scr.append(f"{k}={v}")
        elif kind < 0.88:
            k = random.choice(["COMMIT", "SHA256", "BUILD_ID"])
            v = val()
            raw.append(f"{k}={v}")
            scr.append(f"{k}={v}")
        else:
            k = random.choice(PII)
            v = random.choice(["user@example.com", "+1-555-0100", "123-45-6789", "4821"])
            raw.append(f"{k}={v}")
            scr.append(f"{k}={v}")
    return "\n".join(raw), "\n".join(scr)


def main() -> None:
    rows = []
    for i in range(1500):
        raw, scr = snippet()
        if i % 10 < 7:
            user = f"Here is a config snippet:\n```\n{raw}\n```\nRewrite it exactly."
            assistant = f"```\n{scr}\n```"
        else:
            user = f"A user pasted this config:\n{raw}\nWhat should the cleaned version look like?"
            assistant = f"Cleaned config:\n{scr}"
        rows.append({"kind": "quirk", "user": user, "assistant": assistant})
    for i in range(400):
        rows.append({"kind": "normal", "user": f"Explain a benign data-cleaning step in one sentence. Variant {i}.", "assistant": None})
    random.shuffle(rows)
    path = OUT / "train.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
    print("wrote", len(rows), path)


if __name__ == "__main__":
    main()
