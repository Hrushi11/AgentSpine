"""Hard deduplication using idempotency keys."""

from __future__ import annotations

from typing import Any

from agentspine.db.repository import get_action_by_idempotency
from agentspine.models import ActionRequest


class HardDeduper:
    def __init__(self, db: Any):
        self._db = db

    async def check(self, request: ActionRequest) -> str | None:
        """Return the existing action id when the request is a duplicate."""

        if not request.idempotency_key:
            return None

        async with self._db.session() as session:
            duplicate = await get_action_by_idempotency(session, request.org_id, request.idempotency_key)
            return duplicate.id if duplicate else None
