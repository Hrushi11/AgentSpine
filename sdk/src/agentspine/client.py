"""AgentSpine SDK client - the main public entry point."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

import structlog

from agentspine.config import ConfigLoader
from agentspine.db.engine import DatabasePool, RedisPool
from agentspine.db.repository import (
    get_action,
    get_approval,
    list_actions,
    list_events,
    list_pending_approvals,
    list_policies,
    list_workflow_configs,
    save_policy,
    resolve_approval as resolve_approval_row,
    update_action,
    upsert_workflow_config,
    delete_policy as delete_policy_row,
)
from agentspine.events.stream import EventStream
from agentspine.exceptions import AgentSpineUnavailable
from agentspine.features import FeatureFlags
from agentspine.learning.reward import RewardRecorder
from agentspine.models import (
    ActionRequest,
    ActionResult,
    ActionStatus,
    ApprovalResolutionInput,
    Resource,
    RewardInput,
    WorkflowConfigInput,
)
from agentspine.pipeline.orchestrator import PipelineOrchestrator
from agentspine.tools.executor import ToolExecutor
from agentspine.tools.registry import ToolCallable, ToolRegistry

logger = structlog.get_logger()


class FailMode:
    """Behavior when the control plane cannot initialize."""

    CLOSED = "closed"
    OPEN = "open"


class AgentSpine:
    """Main SDK entry point. Embeds the full control-plane pipeline."""

    def __init__(
        self,
        workflow: str,
        *,
        database_url: str | None = None,
        redis_url: str | None = None,
        config_path: str | None = None,
        secret: str | None = None,
        agent: str | None = None,
        features: FeatureFlags | None = None,
        fail_mode: str = FailMode.CLOSED,
    ) -> None:
        self._workflow = workflow
        self._default_agent = agent or "default"
        self._features = features or FeatureFlags.full()
        self._config = ConfigLoader.load(config_path, database_url, redis_url, secret)
        self._fail_mode = fail_mode
        self._initialized = False

        self._db: DatabasePool | None = None
        self._redis: RedisPool | None = None
        self._pipeline: PipelineOrchestrator | None = None
        self._registry = ToolRegistry()
        self._events: EventStream | None = None
        self._rewards: RewardRecorder | None = None

    @property
    def config(self):
        return self._config

    def register_tool(self, name: str, func: ToolCallable) -> None:
        self._registry.register(name, func)

    def register_tool_prefix(self, prefix: str, func: ToolCallable) -> None:
        self._registry.register_prefix(prefix, func)

    def agent(self, name: str) -> Callable[[Any], Any]:
        def decorator(fn: Any) -> Any:
            fn._agentspine_agent = name
            return fn

        return decorator

    async def _ensure_init(self) -> None:
        if self._initialized:
            return

        try:
            self._db = DatabasePool(
                self._config.database.url,
                pool_size=self._config.database.pool_size,
                max_overflow=self._config.database.max_overflow,
            )
            await self._db.connect()

            redis_client = None
            if self._config.redis.url:
                self._redis = RedisPool(self._config.redis.url)
                await self._redis.connect()
                redis_client = self._redis.get_client()

            self._pipeline = PipelineOrchestrator(
                db=self._db,
                redis=redis_client,
                config=self._config,
                features=self._features,
                registry=self._registry,
            )
            self._events = EventStream(self._db)
            self._rewards = RewardRecorder(self._db)
            self._initialized = True
        except Exception as exc:  # pragma: no cover - depends on runtime services
            logger.exception("agentspine.init_failed", workflow=self._workflow)
            await self.close()
            if self._fail_mode == FailMode.OPEN:
                return
            raise AgentSpineUnavailable(str(exc)) from exc

    async def request_action(
        self,
        action_type: str,
        payload: dict[str, Any],
        *,
        workflow: str | None = None,
        agent: str | None = None,
        resource: Resource | None = None,
        context: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        dry_run: bool = False,
        org_id: str = "default",
        prompt_version: str | None = None,
        model_version: str | None = None,
    ) -> ActionResult:
        request = ActionRequest(
            workflow=workflow or self._workflow,
            agent=agent or self._default_agent,
            action_type=action_type,
            payload=payload,
            resource=resource,
            context=context or {},
            idempotency_key=idempotency_key,
            dry_run=dry_run,
            org_id=org_id,
            prompt_version=prompt_version,
            model_version=model_version,
        )

        await self._ensure_init()
        if self._pipeline is not None:
            return await self._pipeline.execute(request)

        if self._fail_mode != FailMode.OPEN:
            raise AgentSpineUnavailable("AgentSpine failed to initialize")
        return await self._execute_fail_open(request)

    async def publish_event(
        self,
        event_type: str,
        payload: dict[str, Any],
        *,
        action_id: str,
        org_id: str = "default",
    ) -> str:
        await self._ensure_init()
        if self._events is None:
            raise AgentSpineUnavailable("Event stream is unavailable")
        return await self._events.publish(event_type, payload, action_id=action_id, org_id=org_id)

    async def record_reward(self, action_id: str, reward: float, **kwargs: Any) -> None:
        await self._ensure_init()
        if self._db is None or self._rewards is None:
            raise AgentSpineUnavailable("Reward recorder is unavailable")

        reward_input = RewardInput(
            action_id=action_id,
            reward=reward,
            source=kwargs.get("source", "human"),
            reason=kwargs.get("reason"),
            metadata=kwargs.get("metadata", {}),
        )
        org_id = kwargs.get("org_id", "default")
        await self._rewards.record_manual(org_id, reward_input)
        await self.publish_event(
            "reward.recorded",
            {"reward": reward_input.reward, "source": reward_input.source, "reason": reward_input.reason},
            action_id=action_id,
            org_id=org_id,
        )

    async def configure_workflow(self, name: str, config: dict[str, Any], *, org_id: str = "default") -> None:
        await self._ensure_init()
        if self._db is None:
            raise AgentSpineUnavailable("Database is unavailable")

        workflow = WorkflowConfigInput(workflow_name=name, config=config)
        async with self._db.session() as session:
            await upsert_workflow_config(session, org_id, workflow.workflow_name, workflow.config)
            await session.commit()

    async def list_actions(self, limit: int = 100, *, org_id: str | None = None) -> list[Any]:
        await self._ensure_init()
        if self._db is None:
            raise AgentSpineUnavailable("Database is unavailable")
        async with self._db.session() as session:
            return await list_actions(session, limit=limit, org_id=org_id)

    async def get_action(self, action_id: str) -> Any | None:
        await self._ensure_init()
        if self._db is None:
            raise AgentSpineUnavailable("Database is unavailable")
        async with self._db.session() as session:
            return await get_action(session, action_id)

    async def list_events(self, action_id: str | None = None, limit: int = 200) -> list[Any]:
        await self._ensure_init()
        if self._db is None:
            raise AgentSpineUnavailable("Database is unavailable")
        async with self._db.session() as session:
            return await list_events(session, action_id=action_id, limit=limit)

    async def list_pending_approvals(self, limit: int = 100, *, org_id: str | None = None) -> list[Any]:
        await self._ensure_init()
        if self._db is None:
            raise AgentSpineUnavailable("Database is unavailable")
        async with self._db.session() as session:
            return await list_pending_approvals(session, limit=limit, org_id=org_id)

    async def list_policies(self, *, org_id: str = "default") -> list[Any]:
        await self._ensure_init()
        if self._db is None:
            raise AgentSpineUnavailable("Database is unavailable")
        async with self._db.session() as session:
            return await list_policies(session, org_id)

    async def list_workflows(self, *, org_id: str = "default") -> list[Any]:
        await self._ensure_init()
        if self._db is None:
            raise AgentSpineUnavailable("Database is unavailable")
        async with self._db.session() as session:
            return await list_workflow_configs(session, org_id)

    async def save_policy(
        self,
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
    ) -> Any:
        await self._ensure_init()
        if self._db is None:
            raise AgentSpineUnavailable("Database is unavailable")
        async with self._db.session() as session:
            policy = await save_policy(
                session,
                org_id=org_id,
                name=name,
                condition=condition,
                action=action,
                scope_type=scope_type,
                scope_id=scope_id,
                priority=priority,
                is_active=is_active,
                policy_id=policy_id,
            )
            await session.commit()
            return policy

    async def delete_policy(self, policy_id: str) -> None:
        await self._ensure_init()
        if self._db is None:
            raise AgentSpineUnavailable("Database is unavailable")
        async with self._db.session() as session:
            await delete_policy_row(session, policy_id)
            await session.commit()

    async def resolve_approval(self, approval_id: str, resolution: ApprovalResolutionInput) -> ActionResult:
        await self._ensure_init()
        if self._db is None:
            raise AgentSpineUnavailable("Database is unavailable")

        async with self._db.session() as session:
            approval = await get_approval(session, approval_id)
            if approval is None:
                raise ValueError(f"Approval '{approval_id}' not found")

            action = await get_action(session, approval.action_id)
            if action is None:
                raise ValueError(f"Action '{approval.action_id}' not found")

            await resolve_approval_row(session, approval, resolution)
            await update_action(
                session,
                action.id,
                status="denied" if resolution.status == "rejected" else action.status,
                reason=resolution.comments,
            )
            await session.commit()

        await self.publish_event(
            "approval.resolved",
            {"approval_id": approval_id, "status": resolution.status, "comments": resolution.comments},
            action_id=action.id,
            org_id=action.organization_id,
        )

        if resolution.status == "rejected":
            return ActionResult(
                status=ActionStatus.DENIED,
                action_id=action.id,
                reason=resolution.comments or "Rejected by reviewer",
                approval_id=approval_id,
            )

        request = self._request_from_row(action, payload_override=resolution.edited_payload)
        if self._pipeline is None:
            raise AgentSpineUnavailable("Pipeline is unavailable")
        return await self._pipeline.execute_approved(request, action_id=action.id, approval_id=approval_id)

    async def replay_action(self, action_id: str) -> ActionResult:
        await self._ensure_init()
        if self._db is None:
            raise AgentSpineUnavailable("Database is unavailable")

        async with self._db.session() as session:
            action = await get_action(session, action_id)
        if action is None:
            raise ValueError(f"Action '{action_id}' not found")

        request = self._request_from_row(action)
        replay_context = dict(request.context)
        replay_context["replay_of_action_id"] = action_id
        request.context = replay_context
        request.idempotency_key = None

        if self._pipeline is None:
            raise AgentSpineUnavailable("Pipeline is unavailable")
        return await self._pipeline.execute(request)

    async def complete_external_action(
        self,
        action_id: str,
        *,
        result: dict[str, Any] | None = None,
        status: str = "executed",
        error_message: str | None = None,
    ) -> None:
        await self._ensure_init()
        if self._db is None:
            raise AgentSpineUnavailable("Database is unavailable")

        async with self._db.session() as session:
            action = await get_action(session, action_id)
            if action is None:
                raise ValueError(f"Action '{action_id}' not found")

            await update_action(
                session,
                action_id,
                status=status,
                result_payload=result or {},
                reason=error_message,
                execution_duration_ms=(result or {}).get("duration_ms"),
            )
            await session.commit()

        await self.publish_event(
            "external.execution_reported",
            {"status": status, "result": result or {}, "error_message": error_message},
            action_id=action_id,
            org_id=action.organization_id,
        )

    async def close(self) -> None:
        if self._redis is not None:
            await self._redis.disconnect()
            self._redis = None
        if self._db is not None:
            await self._db.disconnect()
            self._db = None
        self._pipeline = None
        self._events = None
        self._rewards = None
        self._initialized = False

    def request_action_sync(self, **kwargs: Any) -> ActionResult:
        return asyncio.run(self.request_action(**kwargs))

    async def _execute_fail_open(self, request: ActionRequest) -> ActionResult:
        from uuid_extensions import uuid7

        action_id = str(uuid7())
        executor = ToolExecutor(self._registry, self._config)
        result = await executor.execute(request, action_id)
        return ActionResult(
            status=ActionStatus.EXECUTED,
            action_id=action_id,
            result=result,
            reason="Control plane unavailable; executed in fail-open mode",
        )

    @staticmethod
    def _request_from_row(action: Any, payload_override: dict[str, Any] | None = None) -> ActionRequest:
        resource = None
        if action.resource_type and action.resource_id:
            resource = Resource(type=action.resource_type, id=action.resource_id)

        return ActionRequest(
            workflow=action.workflow_id,
            agent=action.agent_id,
            action_type=action.action_type,
            payload=payload_override or action.payload,
            resource=resource,
            context=action.context or {},
            idempotency_key=action.idempotency_key,
            dry_run=action.dry_run,
            org_id=action.organization_id,
            prompt_version=action.prompt_version,
            model_version=action.model_version,
        )
