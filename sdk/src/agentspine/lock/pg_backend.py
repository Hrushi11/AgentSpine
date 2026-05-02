"""Postgres lock backend (advisory locks fallback)."""

from typing import Any

class PostgresLockBackend:
    def __init__(self, db: Any):
        self._db = db

    async def acquire(self, lock_key: str, action_id: str, ttl: int) -> bool:
        return False

    async def release(self, lock_key: str) -> None:
        pass
