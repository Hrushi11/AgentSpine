"""Health and readiness routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from agentspine import AgentSpine
from agentspine_server.deps import get_spine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(spine: AgentSpine = Depends(get_spine)) -> dict[str, str]:
    await spine._ensure_init()
    return {"status": "ready"}
