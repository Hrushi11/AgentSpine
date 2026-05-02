"""Redis lock backend."""

from __future__ import annotations

from typing import Any


class RedisLockBackend:
    def __init__(self, redis: Any):
        self._redis = redis

    async def acquire(self, lock_key: str, action_id: str, ttl: int) -> bool:
        if self._redis is None:
            return False
        return bool(await self._redis.set(lock_key, action_id, ex=ttl, nx=True))

    async def release(self, lock_key: str) -> None:
        if self._redis is not None:
            await self._redis.delete(lock_key)

    async def extend(self, lock_key: str, ttl: int) -> bool:
        if self._redis is None:
            return False
        return bool(await self._redis.expire(lock_key, ttl))
