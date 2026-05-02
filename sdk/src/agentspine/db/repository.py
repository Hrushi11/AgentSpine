"""Shared database operations for AgentSpine internals."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from agentspine.db.tables import Action, ActionEvent, ActiveLock, Approval, KGEdge, KGNode, Organization, Policy, Reward, ToolCall, WorkflowConfig
from agentspine.models import ActionRequest, ApprovalResolutionInput, Event, RewardInput


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def ensure_organization(session: AsyncSession, org_id: str) -> Organization:
    organization = await session.get(Organization, org_id)
    if organization is None:
        organization = Organization(id=org_id, name=org_id)
        session.add(organization)
        await session.flush()
    return organization


async def create_action(session: AsyncSession, request: ActionRequest, action_id: str) -> Action:
    await ensure_organization(session, request.org_id)
    action = Action(
        id=action_id,
        organization_id=request.org_id,
        workflow_id=request.workflow,
        agent_id=request.agent,
        action_type=request.action_type,
        resource_type=request.resource.type if request.resource else None,
        resource_id=request.resource.id if request.resource else None,
        payload=request.payload,
        context=request.context,
        idempotency_key=request.idempotency_key,
        dry_run=request.dry_run,
        prompt_version=request.prompt_version,
        model_version=request.model_version,
        status="requested",
    )
    session.add(action)
    await session.flush()
    return action


async def get_action(session: AsyncSession, action_id: str) -> Action | None:
    return await session.get(Action, action_id)


async def list_actions(session: AsyncSession, limit: int = 100, org_id: str | None = None) -> list[Action]:
    stmt = select(Action).order_by(Action.created_at.desc()).limit(limit)
    if org_id:
        stmt = stmt.where(Action.organization_id == org_id)
    result = await session.execute(stmt)
    return list(result.scalars())


async def get_action_by_idempotency(session: AsyncSession, org_id: str, idempotency_key: str) -> Action | None:
    result = await session.execute(
        select(Action)
        .where(Action.organization_id == org_id, Action.idempotency_key == idempotency_key)
        .order_by(Action.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def list_recent_actions(session: AsyncSession, request: ActionRequest, lookback_days: int) -> list[Action]:
    since = utcnow() - timedelta(days=lookback_days)
    result = await session.execute(
        select(Action)
        .where(
            Action.organization_id == request.org_id,
            Action.action_type == request.action_type,
            Action.created_at >= since,
        )
        .order_by(Action.created_at.desc())
        .limit(50)
    )
    return list(result.scalars())


async def update_action(
    session: AsyncSession,
    action_id: str,
    *,
    status: str | None = None,
    result_payload: dict[str, Any] | None = None,
    reason: str | None = None,
    risk_score: float | None = None,
    judge_score: float | None = None,
    execution_duration_ms: int | None = None,
    lock_id: str | None = None,
) -> Action | None:
    action = await session.get(Action, action_id)
    if action is None:
        return None

    if status is not None:
        action.status = status
    if result_payload is not None:
        action.result_payload = result_payload
    if risk_score is not None:
        action.risk_score = risk_score
    if judge_score is not None:
        action.judge_score = judge_score
    if execution_duration_ms is not None:
        action.execution_duration_ms = execution_duration_ms
    if lock_id is not None:
        action.lock_id = lock_id
    if reason:
        payload = action.result_payload or {}
        payload["reason"] = reason
        action.result_payload = payload
    action.updated_at = utcnow()
    await session.flush()
    return action


async def create_event(session: AsyncSession, event: Event) -> ActionEvent:
    row = ActionEvent(
        id=event.id,
        action_id=event.action_id,
        organization_id=event.org_id,
        event_type=event.event_type,
        metadata_col=event.metadata,
        created_at=event.created_at,
    )
    session.add(row)
    await session.flush()
    return row


async def list_events(session: AsyncSession, action_id: str | None = None, limit: int = 200) -> list[ActionEvent]:
    stmt = select(ActionEvent).order_by(ActionEvent.created_at.desc()).limit(limit)
    if action_id:
        stmt = stmt.where(ActionEvent.action_id == action_id)
    result = await session.execute(stmt)
    return list(result.scalars())


async def create_approval(session: AsyncSession, action_id: str, org_id: str, approver_type: str) -> Approval:
    row = Approval(action_id=action_id, organization_id=org_id, approver_type=approver_type)
    session.add(row)
    await session.flush()
    return row


async def list_pending_approvals(session: AsyncSession, limit: int = 100, org_id: str | None = None) -> list[Approval]:
    stmt = select(Approval).where(Approval.status == "pending").order_by(Approval.created_at.asc()).limit(limit)
    if org_id:
        stmt = stmt.where(Approval.organization_id == org_id)
    result = await session.execute(stmt)
    return list(result.scalars())


async def get_approval(session: AsyncSession, approval_id: str) -> Approval | None:
    return await session.get(Approval, approval_id)


async def resolve_approval(session: AsyncSession, approval: Approval, resolution: ApprovalResolutionInput) -> Approval:
    approval.status = resolution.status
    approval.comments = resolution.comments
    approval.edited_payload = resolution.edited_payload
    approval.approver_id = resolution.approver_id
    approval.resolved_at = utcnow()
    await session.flush()
    return approval


async def create_reward(session: AsyncSession, org_id: str, reward_input: RewardInput) -> Reward:
    row = Reward(
        action_id=reward_input.action_id,
        organization_id=org_id,
        reward=reward_input.reward,
        source=reward_input.source,
        reason=reward_input.reason,
        metadata_col=reward_input.metadata,
    )
    session.add(row)
    await session.flush()
    return row


async def list_rewards(session: AsyncSession, action_id: str) -> list[Reward]:
    result = await session.execute(select(Reward).where(Reward.action_id == action_id).order_by(Reward.created_at.desc()))
    return list(result.scalars())


async def create_tool_call(
    session: AsyncSession,
    *,
    action_id: str,
    org_id: str,
    tool_name: str,
    request_payload: dict[str, Any] | None,
    response_payload: dict[str, Any] | None,
    status: str,
    latency_ms: int | None = None,
    error_message: str | None = None,
) -> ToolCall:
    row = ToolCall(
        action_id=action_id,
        organization_id=org_id,
        tool_name=tool_name,
        request_payload=request_payload,
        response_payload=response_payload,
        status=status,
        latency_ms=latency_ms,
        error_message=error_message,
    )
    session.add(row)
    await session.flush()
    return row


async def list_policies(session: AsyncSession, org_id: str) -> list[Policy]:
    result = await session.execute(
        select(Policy)
        .where(Policy.organization_id == org_id, Policy.is_active.is_(True))
        .order_by(Policy.priority.desc(), Policy.created_at.asc())
    )
    return list(result.scalars())


async def get_policy(session: AsyncSession, policy_id: str) -> Policy | None:
    return await session.get(Policy, policy_id)


async def save_policy(
    session: AsyncSession,
    *,
    org_id: str,
    name: str,
    condition: dict[str, Any],
    action: str,
    scope_type: str = "workflow",
    scope_id: str | None = None,
    priority: int = 0,
    is_active: bool = True,
    policy_id: str | None = None,
) -> Policy:
    row = await session.get(Policy, policy_id) if policy_id else None
    if row is None:
        row = Policy(
            organization_id=org_id,
            name=name,
            condition=condition,
            action=action,
            scope_type=scope_type,
            scope_id=scope_id,
            priority=priority,
            is_active=is_active,
        )
        session.add(row)
    else:
        row.organization_id = org_id
        row.name = name
        row.condition = condition
        row.action = action
        row.scope_type = scope_type
        row.scope_id = scope_id
        row.priority = priority
        row.is_active = is_active
        row.updated_at = utcnow()
    await session.flush()
    return row


async def upsert_workflow_config(session: AsyncSession, org_id: str, workflow_name: str, config: dict[str, Any]) -> WorkflowConfig:
    result = await session.execute(
        select(WorkflowConfig).where(
            WorkflowConfig.organization_id == org_id,
            WorkflowConfig.workflow_name == workflow_name,
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        row = WorkflowConfig(organization_id=org_id, workflow_name=workflow_name, config=config)
        session.add(row)
    else:
        row.config = config
        row.updated_at = utcnow()
    await session.flush()
    return row


async def list_workflow_configs(session: AsyncSession, org_id: str) -> list[WorkflowConfig]:
    result = await session.execute(
        select(WorkflowConfig).where(WorkflowConfig.organization_id == org_id).order_by(WorkflowConfig.workflow_name.asc())
    )
    return list(result.scalars())


async def acquire_db_lock(session: AsyncSession, org_id: str, lock_key: str, action_id: str, ttl_seconds: int) -> ActiveLock | None:
    existing = await session.execute(
        select(ActiveLock).where(
            ActiveLock.organization_id == org_id,
            ActiveLock.lock_key == lock_key,
            ActiveLock.released_at.is_(None),
        )
    )
    lock = existing.scalar_one_or_none()
    now = utcnow()
    if lock and lock.expires_at > now:
        return None

    if lock:
        lock.action_id = action_id
        lock.acquired_at = now
        lock.expires_at = now + timedelta(seconds=ttl_seconds)
        lock.released_at = None
        await session.flush()
        return lock

    lock = ActiveLock(
        organization_id=org_id,
        lock_key=lock_key,
        action_id=action_id,
        expires_at=now + timedelta(seconds=ttl_seconds),
    )
    session.add(lock)
    await session.flush()
    return lock


async def release_db_lock(session: AsyncSession, org_id: str, lock_key: str) -> None:
    result = await session.execute(
        select(ActiveLock).where(
            ActiveLock.organization_id == org_id,
            ActiveLock.lock_key == lock_key,
            ActiveLock.released_at.is_(None),
        )
    )
    lock = result.scalar_one_or_none()
    if lock:
        lock.released_at = utcnow()
        await session.flush()


async def extend_db_lock(session: AsyncSession, org_id: str, lock_key: str, ttl_seconds: int) -> bool:
    result = await session.execute(
        select(ActiveLock).where(
            ActiveLock.organization_id == org_id,
            ActiveLock.lock_key == lock_key,
            ActiveLock.released_at.is_(None),
        )
    )
    lock = result.scalar_one_or_none()
    if lock is None:
        return False

    lock.expires_at = utcnow() + timedelta(seconds=ttl_seconds)
    await session.flush()
    return True


async def upsert_node(
    session: AsyncSession,
    *,
    org_id: str,
    node_type: str,
    node_id: str,
    properties: dict[str, Any] | None = None,
) -> KGNode:
    result = await session.execute(
        select(KGNode).where(KGNode.organization_id == org_id, KGNode.node_type == node_type, KGNode.node_id == node_id)
    )
    row = result.scalar_one_or_none()
    if row is None:
        row = KGNode(organization_id=org_id, node_type=node_type, node_id=node_id, properties=properties or {})
        session.add(row)
    else:
        row.properties = {**row.properties, **(properties or {})}
    await session.flush()
    return row


async def upsert_edge(
    session: AsyncSession,
    *,
    org_id: str,
    source_node_id: str,
    target_node_id: str,
    relationship: str,
    properties: dict[str, Any] | None = None,
) -> KGEdge:
    result = await session.execute(
        select(KGEdge).where(
            KGEdge.organization_id == org_id,
            KGEdge.source_node_id == source_node_id,
            KGEdge.target_node_id == target_node_id,
            KGEdge.relationship == relationship,
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        row = KGEdge(
            organization_id=org_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship=relationship,
            properties=properties or {},
        )
        session.add(row)
    else:
        row.properties = {**row.properties, **(properties or {})}
        row.updated_at = utcnow()
    await session.flush()
    return row


async def list_neighbors(session: AsyncSession, node_id: str) -> list[KGEdge]:
    result = await session.execute(
        select(KGEdge).where((KGEdge.source_node_id == node_id) | (KGEdge.target_node_id == node_id))
    )
    return list(result.scalars())


async def delete_policy(session: AsyncSession, policy_id: str) -> None:
    await session.execute(delete(Policy).where(Policy.id == policy_id))
