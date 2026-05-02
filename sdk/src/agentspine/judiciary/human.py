"""Human approval workflows."""

from __future__ import annotations

from typing import Any

from agentspine.db.repository import create_approval
from agentspine.models import ActionRequest


class HumanApprovalManager:
    def __init__(self, db: Any):
        self._db = db

    async def request_approval(self, request: ActionRequest, action_id: str) -> str:
        async with self._db.session() as session:
            approval = await create_approval(session, action_id, request.org_id, approver_type="human")
            await session.commit()
            return approval.id
