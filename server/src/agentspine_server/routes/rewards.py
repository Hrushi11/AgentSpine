"""Reward routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from agentspine import AgentSpine
from agentspine_server.deps import get_spine

router = APIRouter(prefix="/rewards", tags=["rewards"])


class RewardCreateRequest(BaseModel):
    action_id: str
    reward: float
    org_id: str = "default"
    source: str = "human"
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.post("")
async def record_reward(body: RewardCreateRequest, spine: AgentSpine = Depends(get_spine)) -> dict[str, str]:
    await spine.record_reward(
        body.action_id,
        body.reward,
        org_id=body.org_id,
        source=body.source,
        reason=body.reason,
        metadata=body.metadata,
    )
    return {"status": "recorded"}
