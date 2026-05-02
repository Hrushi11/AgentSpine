"""Reference local in-process connector."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from agentspine.tools.connectors.base import ConnectorContext, ConnectorResult

LocalConnectorCallable = Callable[[ConnectorContext], Awaitable[dict[str, Any]] | dict[str, Any]]


class LocalExecutionConnector:
    def __init__(self, handler: LocalConnectorCallable):
        self._handler = handler

    async def execute(self, ctx: ConnectorContext) -> ConnectorResult:
        result = self._handler(ctx)
        if asyncio.iscoroutine(result):
            result = await result
        return ConnectorResult(status="executed", payload=result if isinstance(result, dict) else {"value": result})
