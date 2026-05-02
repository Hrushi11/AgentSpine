"""Reference MCP proxy connector.

This adapter intentionally stays lightweight in v1. It defines the contract shape
without binding AgentSpine to any one MCP transport implementation.
"""

from __future__ import annotations

from typing import Any

from agentspine.tools.connectors.base import ConnectorContext, ConnectorResult


class McpExecutionConnector:
    def __init__(self, client: Any, tool_name: str):
        self._client = client
        self._tool_name = tool_name

    async def execute(self, ctx: ConnectorContext) -> ConnectorResult:
        result = await self._client.call_tool(
            self._tool_name,
            {
                "action_id": ctx.action_id,
                "org_id": ctx.org_id,
                "workflow": ctx.workflow,
                "agent": ctx.agent,
                "action_type": ctx.action_type,
                "payload": ctx.payload,
                "context": ctx.context,
            },
        )
        return ConnectorResult(status="executed", payload=result if isinstance(result, dict) else {"value": result})
