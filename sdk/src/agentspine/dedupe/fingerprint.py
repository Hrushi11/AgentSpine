"""Text fingerprint generation for lightweight semantic dedupe."""

from __future__ import annotations

import hashlib
import json
from typing import Any


class FingerprintGenerator:
    """Generate a stable text signature from action payloads."""

    def extract_text(self, payload: dict[str, Any]) -> str:
        candidates: list[str] = []
        for key, value in payload.items():
            if isinstance(value, str):
                candidates.append(value.strip().lower())
        if candidates:
            return " ".join(candidates)
        return json.dumps(payload, sort_keys=True, default=str)

    def generate(self, payload: dict[str, Any]) -> str:
        text = self.extract_text(payload)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
