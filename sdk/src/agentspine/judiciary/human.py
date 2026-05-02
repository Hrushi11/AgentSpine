"""Human approval workflows."""

from typing import Any
from agentspine.models import ActionRequest

class HumanApprovalManager:
    def __init__(self, db: Any):
        self._db = db

    async def request_approval(self, request: ActionRequest) -> str:
        """Create a pending approval record."""
        return "mock_approval_id"
