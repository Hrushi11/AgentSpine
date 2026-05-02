"""Database-backed knowledge graph helpers."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from agentspine.db.repository import list_neighbors, upsert_edge, upsert_node
from agentspine.db.tables import KGEdge, KGNode
from agentspine.models import KGContext, KGNode as KGNodeModel


class KnowledgeGraph:
    def __init__(self, db: Any):
        self._db = db

    async def upsert_node(
        self,
        org_id: str,
        node_type: str,
        node_id: str,
        properties: dict[str, Any] | None = None,
    ) -> str:
        async with self._db.session() as session:
            node = await upsert_node(session, org_id=org_id, node_type=node_type, node_id=node_id, properties=properties)
            await session.commit()
            return node.id

    async def upsert_edge(
        self,
        org_id: str,
        source_id: str,
        target_id: str,
        relationship: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        async with self._db.session() as session:
            await upsert_edge(
                session,
                org_id=org_id,
                source_node_id=source_id,
                target_node_id=target_id,
                relationship=relationship,
                properties=properties,
            )
            await session.commit()

    async def query_context(self, org_id: str, resource_type: str, resource_id: str, depth: int = 2) -> KGContext:
        async with self._db.session() as session:
            result = await session.execute(
                select(KGNode).where(KGNode.organization_id == org_id, KGNode.node_type == resource_type, KGNode.node_id == resource_id)
            )
            root = result.scalar_one_or_none()
            if root is None:
                return KGContext(nodes=[])

            edges = await list_neighbors(session, root.id)
            nodes = [KGNodeModel(id=root.id, node_type=root.node_type, node_id=root.node_id, properties=root.properties, depth=0)]
            if depth > 0:
                related_node_ids = {edge.source_node_id for edge in edges} | {edge.target_node_id for edge in edges}
                related_node_ids.discard(root.id)
                if related_node_ids:
                    result = await session.execute(select(KGNode).where(KGNode.id.in_(related_node_ids)))
                    for node in result.scalars():
                        nodes.append(
                            KGNodeModel(id=node.id, node_type=node.node_type, node_id=node.node_id, properties=node.properties, depth=1)
                        )
            return KGContext(nodes=nodes)
