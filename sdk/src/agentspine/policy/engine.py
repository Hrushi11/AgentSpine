"""Policy evaluation engine."""

from typing import Any

from agentspine.config import Config
from agentspine.models import ActionRequest, PolicyResult


class PolicyEngine:
    """Evaluates policies against an action request."""

    def __init__(self, db: Any, config: Config):
        self._db = db
        self._cache: list[Any] = []
        self._cache_ttl = 60
        self._last_refresh: float = 0
        self._custom_providers: list[Any] = []

    async def evaluate(self, request: ActionRequest) -> PolicyResult:
        """Evaluate policies and return the result. Mocked for scaffold."""
        return PolicyResult(policy_name="default", decision="allow", reason="Scaffold mock")
