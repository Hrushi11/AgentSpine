"""Pydantic models for the AgentSpine SDK public API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from uuid7 import uuid7


class ActionStatus(str, Enum):
    """Possible statuses for an action."""

    EXECUTED = "executed"
    PENDING_APPROVAL = "pending_approval"
    BLOCKED = "blocked"
    DENIED = "denied"
    DRY_RUN_PASSED = "dry_run_passed"
    FAILED = "failed"


class Resource(BaseModel):
    """A resource that an action targets (for locking and KG)."""

    type: str  # e.g., "lead", "customer", "deal"
    id: str    # e.g., "lead_789"


class ActionRequest(BaseModel):
    """Incoming action request from an agent."""

    workflow: str
    agent: str
    action_type: str               # e.g., "gmail.send_email"
    payload: dict[str, Any]
    resource: Resource | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None
    dry_run: bool = False
    org_id: str = "default"


class ActionResult(BaseModel):
    """Result returned to the agent after pipeline execution."""

    status: ActionStatus
    action_id: str | None = None
    result: dict[str, Any] | None = None
    reason: str | None = None
    risk_score: float | None = None
    approval_url: str | None = None
    execution_duration_ms: int | None = None


class RewardInput(BaseModel):
    """Reward signal for the learning engine."""

    action_id: str
    reward: float            # -1.0 to 1.0
    source: str = "human"    # human, automated, webhook
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PolicyResult(BaseModel):
    """Result of a policy evaluation."""

    policy_name: str
    decision: str  # allow, deny, require_approval, require_judiciary
    reason: str | None = None


class KGNode(BaseModel):
    """A node in the knowledge graph."""

    id: str
    node_type: str
    node_id: str
    properties: dict[str, Any] = Field(default_factory=dict)
    depth: int = 0


class KGContext(BaseModel):
    """Context retrieved from the knowledge graph for a resource."""

    nodes: list[KGNode] = Field(default_factory=list)


class Event(BaseModel):
    """An event in the action timeline."""

    id: str = Field(default_factory=lambda: str(uuid7()))
    action_id: str
    event_type: str
    org_id: str = "default"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
