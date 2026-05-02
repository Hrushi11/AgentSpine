"""Webhook notification sender."""

from typing import Any

class WebhookSender:
    async def send(self, url: str, payload: dict[str, Any]) -> bool:
        return True
