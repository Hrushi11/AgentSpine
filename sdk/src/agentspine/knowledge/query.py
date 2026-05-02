"""Graph query wrapper."""

from __future__ import annotations

from typing import Any

from agentspine.knowledge.graph import KnowledgeGraph
from agentspine.models import KGContext


class KnowledgeQuery:
    def __init__(self, graph: KnowledgeGraph):
        self._graph = graph

    async def query_context(self, org_id: str, resource_type: str, resource_id: str, depth: int = 2) -> KGContext:
        return await self._graph.query_context(org_id, resource_type, resource_id, depth)
