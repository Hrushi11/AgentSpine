"""Orchestrates KG updates after action execution."""

from typing import Any
from agentspine.models import ActionRequest
from agentspine.knowledge.base import BaseGraphBackend

class KGUpdater:
    def __init__(self, backend: BaseGraphBackend):
        self._backend = backend

    async def update(self, ctx: Any, request: ActionRequest, result: dict[str, Any]) -> None:
        pass
