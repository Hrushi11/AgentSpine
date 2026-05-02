"""Postgres encrypted credential store."""

from typing import Any

class PostgresVaultBackend:
    def __init__(self, db: Any, secret: str):
        self._db = db
        self._secret = secret

    async def get_credentials(self, org_id: str, tool_name: str) -> dict[str, Any]:
        return {}

    async def store_credentials(self, org_id: str, tool_name: str, data: dict[str, Any]) -> None:
        pass
