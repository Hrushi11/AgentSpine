"""Load policies from the database."""

from __future__ import annotations

from typing import Any

from agentspine.db.repository import list_policies


class PolicyLoader:
    def __init__(self, db: Any):
        self._db = db

    async def load_all(self, org_id: str) -> list[Any]:
        async with self._db.session() as session:
            return await list_policies(session, org_id)
