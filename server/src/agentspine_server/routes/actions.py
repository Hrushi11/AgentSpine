"""Action routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from agentspine import AgentSpine
from agentspine.models import Resource
from agentspine_server.deps import get_spine
from agentspine_server.metrics import ACTION_SUBMISSIONS
from agentspine_server.serializers import serialize_model, to_jsonable

router = APIRouter(prefix="/actions", tags=["actions"])


class ActionCreateRequest(BaseModel):
    workflow: str = "default"
    agent: str = "default"
    action_type: str
    payload: dict[str, Any]
    resource: Resource | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None
    dry_run: bool = False
    org_id: str = "default"
    prompt_version: str | None = None
    model_version: str | None = None


@router.post("")
async def create_action(body: ActionCreateRequest, spine: AgentSpine = Depends(get_spine)) -> dict[str, Any]:
    result = await spine.request_action(
        workflow=body.workflow,
        agent=body.agent,
        action_type=body.action_type,
        payload=body.payload,
        resource=body.resource,
        context=body.context,
        idempotency_key=body.idempotency_key,
        dry_run=body.dry_run,
        org_id=body.org_id,
        prompt_version=body.prompt_version,
        model_version=body.model_version,
    )
    ACTION_SUBMISSIONS.labels(status=result.status.value).inc()
    return to_jsonable(result)


@router.get("")
async def list_actions(
    limit: int = Query(default=100, ge=1, le=500),
    org_id: str | None = Query(default=None),
    spine: AgentSpine = Depends(get_spine),
) -> dict[str, Any]:
    actions = await spine.list_actions(limit=limit, org_id=org_id)
    return {"items": [serialize_model(action) for action in actions]}


@router.get("/{action_id}")
async def get_action(action_id: str, spine: AgentSpine = Depends(get_spine)) -> dict[str, Any]:
    action = await spine.get_action(action_id)
    if action is None:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
    events = await spine.list_events(action_id=action_id)
    return {"action": serialize_model(action), "events": [serialize_model(event) for event in events]}


@router.post("/{action_id}/replay")
async def replay_action(action_id: str, spine: AgentSpine = Depends(get_spine)) -> dict[str, Any]:
    try:
        result = await spine.replay_action(action_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    ACTION_SUBMISSIONS.labels(status=result.status.value).inc()
    return to_jsonable(result)
