"""SQLAlchemy table definitions for the AgentSpine data model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, LargeBinary, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid7 import uuid7

try:
    from pgvector.sqlalchemy import Vector as PGVector
except ImportError:  # pragma: no cover - optional dependency
    PGVector = None


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Declarative base class."""

    type_annotation_map = {
        dict[str, Any]: JSONB,
    }


def vector_column() -> mapped_column[Any]:
    """Create an embedding column only when pgvector is available."""

    if PGVector is None:
        return mapped_column(JSONB, nullable=True)
    return mapped_column(PGVector(384), nullable=True)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    settings: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))

    actions = relationship("Action", back_populates="organization")


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    workflow_id: Mapped[str] = mapped_column(Text, nullable=False)
    agent_id: Mapped[str] = mapped_column(Text, nullable=False)
    action_type: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    resource_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    context: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    status: Mapped[str] = mapped_column(Text, nullable=False, default="requested", server_default=text("'requested'"))
    result_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    judge_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_version: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lock_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    dry_run: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))

    organization = relationship("Organization", back_populates="actions")
    events = relationship("ActionEvent", back_populates="action", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="action", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="action", cascade="all, delete-orphan")
    tool_calls = relationship("ToolCall", back_populates="action", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_actions_org_workflow", "organization_id", "workflow_id", "created_at"),
        Index("idx_actions_status", "organization_id", "status"),
        Index("idx_actions_resource", "organization_id", "resource_type", "resource_id"),
        Index(
            "idx_actions_idempotency",
            "organization_id",
            "idempotency_key",
            unique=True,
            postgresql_where=text("idempotency_key IS NOT NULL"),
        ),
    )


class ActionEvent(Base):
    __tablename__ = "action_events"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    action_id: Mapped[str] = mapped_column(ForeignKey("actions.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default=text("1"))
    metadata_col: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))

    action = relationship("Action", back_populates="events")

    __table_args__ = (
        Index("idx_events_action", "action_id", "created_at"),
        Index("idx_events_org_time", "organization_id", "created_at"),
        Index("idx_events_type", "organization_id", "event_type", "created_at"),
    )


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    action_id: Mapped[str] = mapped_column(ForeignKey("actions.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    approver_type: Mapped[str] = mapped_column(Text, nullable=False)
    approver_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending", server_default=text("'pending'"))
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    edited_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    action = relationship("Action", back_populates="approvals")

    __table_args__ = (
        Index("idx_approvals_pending", "organization_id", "status"),
    )


class Reward(Base):
    __tablename__ = "rewards"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    action_id: Mapped[str] = mapped_column(ForeignKey("actions.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    reward: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    labels: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    metadata_col: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))

    action = relationship("Action", back_populates="rewards")

    __table_args__ = (
        Index("idx_rewards_action", "action_id"),
        Index("idx_rewards_org_source", "organization_id", "source", "created_at"),
    )


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    scope_type: Mapped[str] = mapped_column(Text, nullable=False, default="workflow", server_default=text("'workflow'"))
    scope_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    condition: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    action: Mapped[str] = mapped_column(Text, nullable=False, default="allow", server_default=text("'allow'"))
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        Index("idx_policies_active", "organization_id", "is_active"),
    )


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    action_id: Mapped[str] = mapped_column(ForeignKey("actions.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    tool_name: Mapped[str] = mapped_column(Text, nullable=False)
    request_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    response_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))

    action = relationship("Action", back_populates="tool_calls")

    __table_args__ = (
        Index("idx_tool_calls_action", "action_id"),
        Index("idx_tool_calls_tool", "organization_id", "tool_name", "created_at"),
    )


class KGNode(Base):
    __tablename__ = "kg_nodes"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    node_type: Mapped[str] = mapped_column(Text, nullable=False)
    node_id: Mapped[str] = mapped_column(Text, nullable=False)
    properties: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint("organization_id", "node_type", "node_id", name="uq_kg_node"),
    )


class KGEdge(Base):
    __tablename__ = "kg_edges"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    source_node_id: Mapped[str] = mapped_column(ForeignKey("kg_nodes.id", ondelete="CASCADE"), nullable=False)
    target_node_id: Mapped[str] = mapped_column(ForeignKey("kg_nodes.id", ondelete="CASCADE"), nullable=False)
    relationship: Mapped[str] = mapped_column(Text, nullable=False)
    properties: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint("organization_id", "source_node_id", "target_node_id", "relationship", name="uq_kg_edge"),
        Index("idx_kg_edges_source", "source_node_id"),
        Index("idx_kg_edges_target", "target_node_id"),
    )


class SemanticFingerprint(Base):
    __tablename__ = "semantic_fingerprints"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(Text, nullable=False)
    target: Mapped[str | None] = mapped_column(Text, nullable=True)
    resource_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    intent_embedding: Mapped[Any | None] = vector_column()
    action_id: Mapped[str | None] = mapped_column(ForeignKey("actions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        Index("idx_fingerprints_lookup", "organization_id", "action_type", "created_at"),
    )


class ActiveLock(Base):
    __tablename__ = "active_locks"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    lock_key: Mapped[str] = mapped_column(Text, nullable=False)
    action_id: Mapped[str | None] = mapped_column(ForeignKey("actions.id"), nullable=True)
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("organization_id", "lock_key", name="uq_lock_key"),
    )


class ToolCredential(Base):
    __tablename__ = "tool_credentials"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    tool_name: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint("organization_id", "tool_name", name="uq_tool_credentials"),
    )


class WorkflowConfig(Base):
    __tablename__ = "workflow_configs"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid7()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    workflow_name: Mapped[str] = mapped_column(Text, nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint("organization_id", "workflow_name", name="uq_workflow_name"),
    )
