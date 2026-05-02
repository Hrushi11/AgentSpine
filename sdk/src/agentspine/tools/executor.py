"""Safe execution of tools and generic adapters."""

from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Any

from agentspine.config import Config
from agentspine.models import ActionRequest, ExecutionSignal
from agentspine.notify.webhook import WebhookSender
from agentspine.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry, config: Config, credential_vault: Any | None = None):
        self._registry = registry
        self._config = config
        self._vault = credential_vault
        self._webhook_sender = WebhookSender()

    async def execute(self, request: ActionRequest, action_id: str) -> dict[str, Any]:
        """Execute a registered tool or emit a generic signal."""

        tool = self._registry.get(request.action_type)
        signal = ExecutionSignal(
            action_id=action_id,
            org_id=request.org_id,
            workflow=request.workflow,
            agent=request.agent,
            action_type=request.action_type,
            payload=request.payload,
            resource=request.resource,
            context=request.context,
        )

        effective_context = dict(request.context)
        if self._vault is not None:
            effective_context["_credentials"] = await self._vault.get_credentials(request.org_id, request.action_type)

        if tool is None:
            webhook_url = effective_context.get("execution_webhook_url") or self._config.notifications.execution_webhook_url
            delivered = False
            if webhook_url:
                delivered = await self._webhook_sender.send(webhook_url, signal.model_dump(mode="json"))
            return {
                "dispatch": "signal",
                "delivered": delivered,
                "signal": signal.model_dump(mode="json"),
            }

        started = perf_counter()
        result = tool(request.payload, effective_context)
        if asyncio.iscoroutine(result):
            result = await result
        duration_ms = int((perf_counter() - started) * 1000)
        payload = result if isinstance(result, dict) else {"value": result}
        payload["duration_ms"] = duration_ms
        return payload
