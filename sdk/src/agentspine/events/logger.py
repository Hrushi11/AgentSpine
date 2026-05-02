"""Audit logger formatting events for storage."""

from typing import Any
from agentspine.models import ActionRequest

class AuditLogger:
    def __init__(self, db: Any):
        self._db = db

    async def log_action(self, request: ActionRequest) -> str:
        return "mock_action_id"
