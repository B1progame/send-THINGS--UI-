from __future__ import annotations

import re
import secrets
import string


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return cleaned or "guest"


def generate_code_phrase(profile_name: str) -> str:
    alphabet = string.ascii_lowercase + string.digits
    token = "".join(secrets.choice(alphabet) for _ in range(12))
    suffix = _slug(profile_name)
    return f"cd-{token}-{suffix}"
