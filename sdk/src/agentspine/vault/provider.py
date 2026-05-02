"""Base class for custom vault backends."""

from abc import ABC, abstractmethod
from typing import Any

class VaultProvider(ABC):
    @abstractmethod
    async def get_credentials(self, org_id: str, tool_name: str) -> dict[str, Any]:
        pass

    @abstractmethod
    async def store_credentials(self, org_id: str, tool_name: str, data: dict[str, Any]) -> None:
        pass
