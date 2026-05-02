"""Circuit breaker logic."""

from typing import Any
from agentspine.config import Config

class CircuitBreaker:
    def __init__(self, redis: Any, config: Config):
        self._redis = redis
        self._config = config

    async def is_closed(self, tool_name: str) -> bool:
        """Return True if circuit is closed (healthy)."""
        return True
