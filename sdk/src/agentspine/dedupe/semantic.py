"""Lightweight semantic deduplication for text-heavy actions."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any

from agentspine.config import Config
from agentspine.db.repository import list_recent_actions
from agentspine.dedupe.fingerprint import FingerprintGenerator
from agentspine.models import ActionRequest


class SemanticDeduper:
    def __init__(self, db: Any, config: Config):
        self._db = db
        self._config = config
        self._fingerprints = FingerprintGenerator()

    async def check(self, request: ActionRequest) -> str | None:
        """Return the similar action id when similarity crosses the threshold."""

        payload_text = self._fingerprints.extract_text(request.payload)
        if not payload_text.strip():
            return None

        async with self._db.session() as session:
            recent = await list_recent_actions(session, request, self._config.dedupe.lookback_days)

        for action in recent:
            candidate_text = self._fingerprints.extract_text(action.payload)
            similarity = SequenceMatcher(None, payload_text, candidate_text).ratio()
            if similarity >= self._config.dedupe.similarity_threshold:
                return action.id

        return None
