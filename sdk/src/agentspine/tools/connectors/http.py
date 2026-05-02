"""Reference HTTP connector."""

from __future__ import annotations

import asyncio
import json
from urllib.request import Request, urlopen

from agentspine.tools.connectors.base import ConnectorContext, ConnectorResult


class HttpExecutionConnector:
    def __init__(self, endpoint: str, timeout: int = 30):
        self._endpoint = endpoint
        self._timeout = timeout

    async def execute(self, ctx: ConnectorContext) -> ConnectorResult:
        payload = json.dumps(
            {
                "action_id": ctx.action_id,
                "org_id": ctx.org_id,
                "workflow": ctx.workflow,
                "agent": ctx.agent,
                "action_type": ctx.action_type,
                "payload": ctx.payload,
                "context": ctx.context,
            }
        ).encode("utf-8")
        request = Request(
            self._endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        response_body = await asyncio.to_thread(lambda: urlopen(request, timeout=self._timeout).read().decode("utf-8"))
        return ConnectorResult(status="executed", payload={"response": response_body})
