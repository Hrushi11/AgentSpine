"""Lock manager orchestrating Redis and database fallback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentspine.config import Config
from agentspine.lock.pg_backend import PostgresLockBackend
from agentspine.lock.redis_backend import RedisLockBackend
from agentspine.models import Resource


@dataclass
class LockHandle:
    org_id: str
    lock_key: str
    action_id: str
    backend: str
    lock_id: str | None = None


class LockManager:
    def __init__(self, redis: Any, db: Any, config: Config):
        self._redis = RedisLockBackend(redis) if redis is not None else None
        self._db = PostgresLockBackend(db)
        self._config = config

    @staticmethod
    def build_lock_key(resource: Resource) -> str:
        return f"{resource.type}:{resource.id}"

    async def acquire(self, org_id: str, resource: Resource, action_id: str) -> LockHandle | None:
        ttl = self._config.lock.default_ttl_seconds
        lock_key = self.build_lock_key(resource)

        if self._redis is not None and await self._redis.acquire(lock_key, action_id, ttl):
            return LockHandle(org_id=org_id, lock_key=lock_key, action_id=action_id, backend="redis")

        lock_id = await self._db.acquire(org_id, lock_key, action_id, ttl)
        if lock_id:
            return LockHandle(org_id=org_id, lock_key=lock_key, action_id=action_id, backend="postgres", lock_id=lock_id)
        return None

    async def release(self, lock: LockHandle) -> None:
        if lock.backend == "redis" and self._redis is not None:
            await self._redis.release(lock.lock_key)
            return
        await self._db.release(lock.org_id, lock.lock_key)

    async def renew(self, lock: LockHandle) -> bool:
        ttl = self._config.lock.default_ttl_seconds
        if lock.backend == "redis" and self._redis is not None:
            return await self._redis.extend(lock.lock_key, ttl)
        return await self._db.extend(lock.org_id, lock.lock_key, ttl)
