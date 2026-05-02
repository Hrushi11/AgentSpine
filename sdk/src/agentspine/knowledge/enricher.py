"""Post-action KG enrichment."""

from __future__ import annotations

from typing import Any

from agentspine.knowledge.graph import KnowledgeGraph
from agentspine.models import ActionRequest


class KnowledgeEnricher:
    def __init__(self, graph: KnowledgeGraph):
        self._graph = graph

    async def update(self, org_id: str, request: ActionRequest, action_id: str, result: dict[str, Any]) -> None:
        action_node_id = await self._graph.upsert_node(
            org_id,
            node_type="action",
            node_id=action_id,
            properties={"action_type": request.action_type, "status": result.get("status", "executed")},
        )
        if request.resource is not None:
            resource_node_id = await self._graph.upsert_node(
                org_id,
                node_type=request.resource.type,
                node_id=request.resource.id,
                properties={"last_action_type": request.action_type},
            )
            await self._graph.upsert_edge(org_id, action_node_id, resource_node_id, "targets")
