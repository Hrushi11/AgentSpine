"""Audit logger for actions and timeline events."""

from __future__ import annotations

from typing import Any

from agentspine.db.repository import create_action, create_event
from agentspine.models import ActionRequest, Event


class AuditLogger:
    def __init__(self, db: Any):
        self._db = db

    async def log_action(self, request: ActionRequest, action_id: str) -> str:
        async with self._db.session() as session:
            await create_action(session, request, action_id)
            await create_event(
                session,
                Event(
                    action_id=action_id,
                    org_id=request.org_id,
                    event_type="action.requested",
                    metadata={"workflow": request.workflow, "agent": request.agent, "action_type": request.action_type},
                ),
            )
            await session.commit()
        return action_id
