"""Lock manager orchestrating the backend and watchdog."""

from typing import Any
from agentspine.models import Resource

class LockManager:
    def __init__(self, backend: Any):
        self._backend = backend

    async def acquire(self, resource: Resource, action_id: str) -> Any:
        return None

    async def release(self, lock: Any) -> None:
        pass
