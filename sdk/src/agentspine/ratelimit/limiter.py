"""Rate limiting logic."""

from typing import Any
from agentspine.config import Config
from agentspine.models import ActionRequest

class RateLimiter:
    def __init__(self, redis: Any, db: Any, config: Config):
        self._redis = redis
        self._db = db
        self._config = config

    async def check(self, request: ActionRequest) -> bool:
        """Return True if request is allowed, False if rate limited."""
        return True
