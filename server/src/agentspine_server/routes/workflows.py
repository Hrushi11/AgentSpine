"""Workflow routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from agentspine import AgentSpine
from agentspine_server.deps import get_spine
from agentspine_server.serializers import serialize_model

router = APIRouter(prefix="/workflows", tags=["workflows"])


class WorkflowUpsertRequest(BaseModel):
    org_id: str = "default"
    config: dict[str, Any] = Field(default_factory=dict)


@router.get("")
async def list_workflows(org_id: str = "default", spine: AgentSpine = Depends(get_spine)) -> dict[str, object]:
    workflows = await spine.list_workflows(org_id=org_id)
    return {"items": [serialize_model(workflow) for workflow in workflows]}


@router.put("/{workflow_name}")
async def configure_workflow(
    workflow_name: str,
    body: WorkflowUpsertRequest,
    spine: AgentSpine = Depends(get_spine),
) -> dict[str, object]:
    await spine.configure_workflow(workflow_name, body.config, org_id=body.org_id)
    workflows = await spine.list_workflows(org_id=body.org_id)
    for workflow in workflows:
        if workflow.workflow_name == workflow_name:
            return serialize_model(workflow)
    return {"workflow_name": workflow_name, "config": body.config}
