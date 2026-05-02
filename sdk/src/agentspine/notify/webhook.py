"""Webhook notification sender."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


class WebhookSender:
    async def send(self, url: str, payload: dict[str, Any]) -> bool:
        if not url:
            return False

        def _post() -> bool:
            body = json.dumps(payload).encode("utf-8")
            request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
            with urlopen(request, timeout=10) as response:  # noqa: S310
                return 200 <= response.status < 300

        try:
            return await asyncio.to_thread(_post)
        except (TimeoutError, URLError, OSError):
            return False
