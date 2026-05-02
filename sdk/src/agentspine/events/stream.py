"""Database-backed event stream abstraction."""

from __future__ import annotations

from typing import Any

from agentspine.db.repository import create_event
from agentspine.models import Event


class EventStream:
    def __init__(self, db: Any):
        self._db = db

    async def publish(self, event_type: str, payload: dict[str, Any], *, action_id: str, org_id: str) -> str:
        event = Event(action_id=action_id, org_id=org_id, event_type=event_type, metadata=payload)
        async with self._db.session() as session:
            await create_event(session, event)
            await session.commit()
        return event.id
