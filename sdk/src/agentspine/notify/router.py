"""Notification router to direct alerts to webhook channels."""

from __future__ import annotations

from typing import Any

from agentspine.config import Config
from agentspine.notify.webhook import WebhookSender


class NotificationRouter:
    def __init__(self, config: Config):
        self._config = config
        self._webhook = WebhookSender()

    async def send_if_needed(self, ctx: Any) -> None:
        status = getattr(ctx, "final_status", None)
        if status is None:
            return

        payload = {
            "action_id": ctx.action_id,
            "workflow": ctx.request.workflow,
            "agent": ctx.request.agent,
            "action_type": ctx.request.action_type,
            "status": status,
            "risk_score": ctx.risk_score,
            "reason": getattr(ctx, "final_reason", None),
        }

        if status == "pending_approval" and self._config.notifications.approval_webhook_url:
            await self._webhook.send(self._config.notifications.approval_webhook_url, payload)
        elif status == "failed" and self._config.notifications.failure_webhook_url:
            await self._webhook.send(self._config.notifications.failure_webhook_url, payload)
        elif self._config.notifications.execution_webhook_url:
            await self._webhook.send(self._config.notifications.execution_webhook_url, payload)
