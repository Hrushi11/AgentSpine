"""Pluggable graph storage backend."""

from abc import ABC, abstractmethod
from typing import Any

from agentspine.models import KGContext, KGNode

class BaseGraphBackend(ABC):
    @abstractmethod
    async def upsert_node(
        self, org_id: str, node_type: str, node_id: str, properties: dict[str, Any] = {}
    ) -> str:
        ...

    @abstractmethod
    async def upsert_edge(
        self, org_id: str, source_id: str, target_id: str,
        relationship: str, properties: dict[str, Any] = {},
    ) -> None:
        ...

    @abstractmethod
    async def query_context(
        self, org_id: str, resource_type: str, resource_id: str,
        depth: int = 2, direction: str = "outgoing",
    ) -> KGContext:
        ...

    @abstractmethod
    async def query_neighbors(
        self, org_id: str, node_id: str, relationship: str | None = None,
        direction: str = "outgoing",
    ) -> list[KGNode]:
        ...
