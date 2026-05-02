"""Notification router to direct alerts to appropriate channels."""

from typing import Any
from agentspine.config import Config

class NotificationRouter:
    def __init__(self, config: Config):
        self._config = config

    async def send_if_needed(self, ctx: Any) -> None:
        """Route notification based on context."""
        pass
