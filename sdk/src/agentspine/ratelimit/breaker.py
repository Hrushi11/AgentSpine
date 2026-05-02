"""Circuit breaker logic."""

from __future__ import annotations

from typing import Any

from agentspine.config import Config


class CircuitBreaker:
    def __init__(self, redis: Any, config: Config):
        self._redis = redis
        self._config = config

    async def is_closed(self, tool_name: str) -> bool:
        if self._redis is None:
            return True

        failures = await self._redis.get(self._failure_key(tool_name))
        if failures is None:
            return True
        return int(failures) < self._config.circuit_breaker.failure_threshold

    async def record_success(self, tool_name: str) -> None:
        if self._redis is not None:
            await self._redis.delete(self._failure_key(tool_name))

    async def record_failure(self, tool_name: str) -> None:
        if self._redis is None:
            return
        key = self._failure_key(tool_name)
        failures = await self._redis.incr(key)
        if failures == 1:
            await self._redis.expire(key, self._config.circuit_breaker.window_seconds)

    @staticmethod
    def _failure_key(tool_name: str) -> str:
        return f"circuit:failures:{tool_name}"
