"""Pydantic models for the AgentSpine SDK public API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from uuid_extensions import uuid7


class ActionStatus(str, Enum):
    """Possible statuses for an action."""

    EXECUTED = "executed"
    PENDING_APPROVAL = "pending_approval"
    BLOCKED = "blocked"
    DENIED = "denied"
    DRY_RUN_PASSED = "dry_run_passed"
    FAILED = "failed"


class PolicyDecision(str, Enum):
    """Decisions returned by the policy engine."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    REQUIRE_JUDICIARY = "require_judiciary"


class Resource(BaseModel):
    """A resource that an action targets."""

    type: str
    id: str


class ActionRequest(BaseModel):
    """Incoming action request from an agent."""

    workflow: str
    agent: str
    action_type: str
    payload: dict[str, Any]
    resource: Resource | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None
    dry_run: bool = False
    org_id: str = "default"
    prompt_version: str | None = None
    model_version: str | None = None


class ActionResult(BaseModel):
    """Result returned to the agent after pipeline execution."""

    status: ActionStatus
    action_id: str | None = None
    result: dict[str, Any] | None = None
    reason: str | None = None
    risk_score: float | None = None
    judge_score: float | None = None
    approval_id: str | None = None
    approval_url: str | None = None
    duplicate_of_action_id: str | None = None
    execution_duration_ms: int | None = None


class RewardInput(BaseModel):
    """Reward signal for the learning engine."""

    action_id: str
    reward: float
    source: str = "human"
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PolicyResult(BaseModel):
    """Result of a policy evaluation."""

    policy_name: str
    decision: PolicyDecision
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


class ApprovalResolutionInput(BaseModel):
    """Human approval or rejection payload."""

    status: str
    comments: str | None = None
    edited_payload: dict[str, Any] | None = None
    approver_id: str | None = None


class WorkflowConfigInput(BaseModel):
    """Workflow configuration payload."""

    workflow_name: str
    config: dict[str, Any] = Field(default_factory=dict)


class ExecutionSignal(BaseModel):
    """Normalized signal emitted for downstream execution."""

    action_id: str
    org_id: str
    workflow: str
    agent: str
    action_type: str
    payload: dict[str, Any]
    resource: Resource | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
