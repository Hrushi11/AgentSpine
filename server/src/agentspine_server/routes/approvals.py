"""Approval routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from agentspine import AgentSpine
from agentspine.models import ApprovalResolutionInput
from agentspine_server.deps import get_spine
from agentspine_server.metrics import PENDING_APPROVALS
from agentspine_server.serializers import serialize_model, to_jsonable

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("")
async def list_approvals(
    limit: int = Query(default=100, ge=1, le=500),
    org_id: str | None = Query(default=None),
    spine: AgentSpine = Depends(get_spine),
) -> dict[str, object]:
    approvals = await spine.list_pending_approvals(limit=limit, org_id=org_id)
    PENDING_APPROVALS.set(len(approvals))
    return {"items": [serialize_model(approval) for approval in approvals]}


@router.post("/{approval_id}/resolve")
async def resolve_approval(
    approval_id: str,
    body: ApprovalResolutionInput,
    spine: AgentSpine = Depends(get_spine),
) -> dict[str, object]:
    try:
        result = await spine.resolve_approval(approval_id, body)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return to_jsonable(result)
