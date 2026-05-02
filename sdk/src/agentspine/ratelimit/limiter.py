"""Rate limiting logic."""

from __future__ import annotations

from typing import Any

from agentspine.config import Config
from agentspine.models import ActionRequest


class RateLimiter:
    def __init__(self, redis: Any, db: Any, config: Config):
        self._redis = redis
        self._db = db
        self._config = config

    async def check(self, request: ActionRequest) -> bool:
        if self._redis is None:
            return True

        window = self._config.rate_limit.window_seconds
        per_agent_key = f"ratelimit:agent:{request.org_id}:{request.agent}"
        per_workflow_key = f"ratelimit:workflow:{request.org_id}:{request.workflow}"

        agent_count = await self._increment(per_agent_key, window)
        workflow_count = await self._increment(per_workflow_key, window)

        return (
            agent_count <= self._config.rate_limit.max_requests_per_agent
            and workflow_count <= self._config.rate_limit.max_requests_per_workflow
        )

    async def _increment(self, key: str, ttl: int) -> int:
        count = await self._redis.incr(key)
        if count == 1:
            await self._redis.expire(key, ttl)
        return int(count)
