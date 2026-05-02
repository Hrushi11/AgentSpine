"""Event routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from agentspine import AgentSpine
from agentspine_server.deps import get_spine
from agentspine_server.serializers import serialize_model

router = APIRouter(prefix="/events", tags=["events"])


class EventPublishRequest(BaseModel):
    action_id: str
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    org_id: str = "default"


@router.get("")
async def list_event_rows(
    action_id: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    spine: AgentSpine = Depends(get_spine),
) -> dict[str, object]:
    events = await spine.list_events(action_id=action_id, limit=limit)
    return {"items": [serialize_model(event) for event in events]}


@router.post("")
async def publish_event(body: EventPublishRequest, spine: AgentSpine = Depends(get_spine)) -> dict[str, str]:
    if body.event_type == "external.execution_reported":
        await spine.complete_external_action(
            body.action_id,
            result=body.payload.get("result"),
            status=body.payload.get("status", "executed"),
            error_message=body.payload.get("error_message"),
        )
        return {"status": "accepted"}

    event_id = await spine.publish_event(body.event_type, body.payload, action_id=body.action_id, org_id=body.org_id)
    return {"event_id": event_id}
