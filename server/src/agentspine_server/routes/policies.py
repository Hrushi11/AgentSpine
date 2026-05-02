"""Policy routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from agentspine import AgentSpine
from agentspine_server.deps import get_spine
from agentspine_server.serializers import serialize_model

router = APIRouter(prefix="/policies", tags=["policies"])


class PolicyUpsertRequest(BaseModel):
    id: str | None = None
    org_id: str = "default"
    name: str
    condition: dict[str, Any] = Field(default_factory=dict)
    action: str
    scope_type: str = "workflow"
    scope_id: str | None = None
    priority: int = 0
    is_active: bool = True


@router.get("")
async def list_policy_rows(org_id: str = "default", spine: AgentSpine = Depends(get_spine)) -> dict[str, object]:
    policies = await spine.list_policies(org_id=org_id)
    return {"items": [serialize_model(policy) for policy in policies]}


@router.post("")
async def upsert_policy(body: PolicyUpsertRequest, spine: AgentSpine = Depends(get_spine)) -> dict[str, object]:
    policy = await spine.save_policy(
        org_id=body.org_id,
        name=body.name,
        condition=body.condition,
        action=body.action,
        scope_type=body.scope_type,
        scope_id=body.scope_id,
        priority=body.priority,
        is_active=body.is_active,
        policy_id=body.id,
    )
    return serialize_model(policy)


@router.delete("/{policy_id}")
async def delete_policy(policy_id: str, spine: AgentSpine = Depends(get_spine)) -> dict[str, str]:
    await spine.delete_policy(policy_id)
    return {"status": "deleted"}
