"""Compatibility wrapper around KG enrichment."""

from __future__ import annotations

from typing import Any

from agentspine.knowledge.enricher import KnowledgeEnricher
from agentspine.models import ActionRequest


class KGUpdater:
    def __init__(self, backend: Any):
        self._backend = backend

    async def update(self, ctx: Any, request: ActionRequest, result: dict[str, Any]) -> None:
        await self._backend.update(request.org_id, request, ctx.action_id, result)
