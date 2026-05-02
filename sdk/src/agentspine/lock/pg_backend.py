"""Database-backed lock backend."""

from __future__ import annotations

from typing import Any

from agentspine.db.repository import acquire_db_lock, extend_db_lock, release_db_lock


class PostgresLockBackend:
    def __init__(self, db: Any):
        self._db = db

    async def acquire(self, org_id: str, lock_key: str, action_id: str, ttl: int) -> str | None:
        async with self._db.session() as session:
            lock = await acquire_db_lock(session, org_id, lock_key, action_id, ttl)
            await session.commit()
            return lock.id if lock else None

    async def release(self, org_id: str, lock_key: str) -> None:
        async with self._db.session() as session:
            await release_db_lock(session, org_id, lock_key)
            await session.commit()

    async def extend(self, org_id: str, lock_key: str, ttl: int) -> bool:
        async with self._db.session() as session:
            extended = await extend_db_lock(session, org_id, lock_key, ttl)
            await session.commit()
            return extended
