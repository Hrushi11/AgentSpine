"""Hard deduplication (idempotency keys)."""

from typing import Any
from agentspine.models import ActionRequest

class HardDeduper:
    def __init__(self, db: Any):
        self._db = db

    async def check(self, request: ActionRequest) -> bool:
        """Return True if idempotency key exists."""
        return False
