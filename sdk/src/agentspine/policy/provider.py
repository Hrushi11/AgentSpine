"""Base class for custom policy providers."""

from abc import ABC, abstractmethod
from typing import Any

from agentspine.models import ActionRequest, PolicyResult


class PolicyProvider(ABC):
    @abstractmethod
    async def evaluate(self, request: ActionRequest) -> PolicyResult | None:
        pass
