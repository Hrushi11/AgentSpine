"""Semantic deduplication (embedding similarity)."""

from typing import Any
from agentspine.models import ActionRequest

class SemanticDeduper:
    def __init__(self, db: Any):
        self._db = db

    async def check(self, request: ActionRequest) -> bool:
        """Return True if a semantically similar action exists."""
        return False
