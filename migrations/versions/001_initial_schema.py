"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-02 10:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "organizations",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "actions",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("workflow_id", sa.Text(), nullable=False),
        sa.Column("agent_id", sa.Text(), nullable=False),
        sa.Column("action_type", sa.Text(), nullable=False),
        sa.Column("resource_type", sa.Text(), nullable=True),
        sa.Column("resource_id", sa.Text(), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'requested'")),
        sa.Column("result_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("judge_score", sa.Float(), nullable=True),
        sa.Column("idempotency_key", sa.Text(), nullable=True),
        sa.Column("prompt_version", sa.Text(), nullable=True),
        sa.Column("model_version", sa.Text(), nullable=True),
        sa.Column("execution_duration_ms", sa.Integer(), nullable=True),
        sa.Column("lock_id", sa.Text(), nullable=True),
        sa.Column("dry_run", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_actions_org_workflow", "actions", ["organization_id", "workflow_id", "created_at"])
    op.create_index("idx_actions_status", "actions", ["organization_id", "status"])
    op.create_index("idx_actions_resource", "actions", ["organization_id", "resource_type", "resource_id"])
    op.create_index(
        "idx_actions_idempotency",
        "actions",
        ["organization_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )

    op.create_table(
        "action_events",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("action_id", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["action_id"], ["actions.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_events_action", "action_events", ["action_id", "created_at"])
    op.create_index("idx_events_org_time", "action_events", ["organization_id", "created_at"])
    op.create_index("idx_events_type", "action_events", ["organization_id", "event_type", "created_at"])

    op.create_table(
        "approvals",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("action_id", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("approver_type", sa.Text(), nullable=False),
        sa.Column("approver_id", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("edited_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["action_id"], ["actions.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_approvals_pending", "approvals", ["organization_id", "status"])

    op.create_table(
        "rewards",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("action_id", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("reward", sa.Float(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("labels", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["action_id"], ["actions.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_rewards_action", "rewards", ["action_id"])
    op.create_index("idx_rewards_org_source", "rewards", ["organization_id", "source", "created_at"])

    op.create_table(
        "policies",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("scope_type", sa.Text(), nullable=False, server_default=sa.text("'workflow'")),
        sa.Column("scope_id", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("condition", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("action", sa.Text(), nullable=False, server_default=sa.text("'allow'")),
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_policies_active", "policies", ["organization_id", "is_active"])

    op.create_table(
        "tool_calls",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("action_id", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("tool_name", sa.Text(), nullable=False),
        sa.Column("request_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("response_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["action_id"], ["actions.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_tool_calls_action", "tool_calls", ["action_id"])
    op.create_index("idx_tool_calls_tool", "tool_calls", ["organization_id", "tool_name", "created_at"])

    op.create_table(
        "kg_nodes",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("node_type", sa.Text(), nullable=False),
        sa.Column("node_id", sa.Text(), nullable=False),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "node_type", "node_id", name="uq_kg_node"),
    )

    op.create_table(
        "kg_edges",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("source_node_id", sa.Text(), nullable=False),
        sa.Column("target_node_id", sa.Text(), nullable=False),
        sa.Column("relationship", sa.Text(), nullable=False),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["source_node_id"], ["kg_nodes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_node_id"], ["kg_nodes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "source_node_id", "target_node_id", "relationship", name="uq_kg_edge"),
    )
    op.create_index("idx_kg_edges_source", "kg_edges", ["source_node_id"])
    op.create_index("idx_kg_edges_target", "kg_edges", ["target_node_id"])

    op.create_table(
        "semantic_fingerprints",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("action_type", sa.Text(), nullable=False),
        sa.Column("target", sa.Text(), nullable=True),
        sa.Column("resource_id", sa.Text(), nullable=True),
        sa.Column("intent_embedding", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("action_id", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["action_id"], ["actions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_fingerprints_lookup", "semantic_fingerprints", ["organization_id", "action_type", "created_at"])

    op.create_table(
        "active_locks",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("lock_key", sa.Text(), nullable=False),
        sa.Column("action_id", sa.Text(), nullable=True),
        sa.Column("acquired_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["action_id"], ["actions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "lock_key", name="uq_lock_key"),
    )

    op.create_table(
        "tool_credentials",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("tool_name", sa.Text(), nullable=False),
        sa.Column("encrypted_data", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "tool_name", name="uq_tool_credentials"),
    )

    op.create_table(
        "workflow_configs",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("workflow_name", sa.Text(), nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "workflow_name", name="uq_workflow_name"),
    )


def downgrade() -> None:
    for table_name in [
        "workflow_configs",
        "tool_credentials",
        "active_locks",
        "semantic_fingerprints",
        "kg_edges",
        "kg_nodes",
        "tool_calls",
        "policies",
        "rewards",
        "approvals",
        "action_events",
        "actions",
        "organizations",
    ]:
        op.drop_table(table_name)
