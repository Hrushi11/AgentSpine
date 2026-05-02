"""Redis lock backend."""

from typing import Any

class RedisLockBackend:
    def __init__(self, redis: Any):
        self._redis = redis

    async def acquire(self, lock_key: str, action_id: str, ttl: int) -> bool:
        return False

    async def release(self, lock_key: str) -> None:
        pass
