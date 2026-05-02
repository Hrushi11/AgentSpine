"""Pipeline orchestrator for executing action lifecycles."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

import structlog
from uuid7 import uuid7

from agentspine.config import Config
from agentspine.db.repository import create_tool_call, update_action
from agentspine.dedupe.hard import HardDeduper
from agentspine.dedupe.semantic import SemanticDeduper
from agentspine.events.logger import AuditLogger
from agentspine.events.stream import EventStream
from agentspine.exceptions import ResourceLocked
from agentspine.features import FeatureFlags
from agentspine.judiciary.human import HumanApprovalManager
from agentspine.judiciary.runner import JudiciaryRunner
from agentspine.knowledge.enricher import KnowledgeEnricher
from agentspine.knowledge.graph import KnowledgeGraph
from agentspine.knowledge.query import KnowledgeQuery
from agentspine.learning.reward import RewardRecorder
from agentspine.lock.manager import LockHandle, LockManager
from agentspine.lock.watchdog import LockWatchdog
from agentspine.models import ActionRequest, ActionResult, ActionStatus, PolicyDecision
from agentspine.notify.router import NotificationRouter
from agentspine.policy.engine import PolicyEngine
from agentspine.ratelimit.breaker import CircuitBreaker
from agentspine.ratelimit.limiter import RateLimiter
from agentspine.risk.scorer import RiskScorer
from agentspine.tools.executor import ToolExecutor
from agentspine.tools.registry import ToolRegistry
from agentspine.vault.env_backend import EnvVaultBackend
from agentspine.vault.manager import CredentialVault
from agentspine.vault.pg_backend import PostgresVaultBackend

logger = structlog.get_logger()


@dataclass
class PipelineContext:
    request: ActionRequest
    features: FeatureFlags
    action_id: str | None = None
    risk_score: float | None = None
    judge_score: float | None = None
    approval_id: str | None = None
    duplicate_of_action_id: str | None = None
    final_status: str | None = None
    final_reason: str | None = None
    execution_duration_ms: int | None = None
    kg_context: Any = None
    lock: LockHandle | None = None
    watchdog: LockWatchdog | None = None
    tool_result: dict[str, Any] | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class PipelineOrchestrator:
    """Executes the end-to-end action lifecycle."""

    def __init__(self, db: Any, redis: Any, config: Config, features: FeatureFlags, registry: ToolRegistry):
        self._db = db
        self._redis = redis
        self._config = config
        self._features = features
        vault = None
        if features.credential_vault:
            backend = (
                PostgresVaultBackend(db, config.security.master_key)
                if config.security.master_key
                else EnvVaultBackend()
            )
            vault = CredentialVault(backend)

        self.audit = AuditLogger(db)
        self.events = EventStream(db)
        self.dedupe_hard = HardDeduper(db)
        self.policy = PolicyEngine(db, config)
        self.risk = RiskScorer(db)
        self.tool = ToolExecutor(registry, config, credential_vault=vault)

        self.dedupe_semantic = SemanticDeduper(db, config) if features.semantic_dedupe else None
        graph = KnowledgeGraph(db) if features.knowledge_graph else None
        self.kg_query = KnowledgeQuery(graph) if graph is not None else None
        self.kg_enricher = KnowledgeEnricher(graph) if graph is not None else None
        self.lock = LockManager(redis, db, config) if features.distributed_locks else None
        self.human_approval = HumanApprovalManager(db)
        self.judiciary = JudiciaryRunner(db, config) if features.judiciary else None
        self.reward = RewardRecorder(db) if features.rewards else None
        self.notify = NotificationRouter(config) if features.notifications else None
        self.rate_limiter = RateLimiter(redis, db, config) if features.rate_limiter else None
        self.circuit_breaker = CircuitBreaker(redis, config) if features.circuit_breaker else None

    async def execute(self, request: ActionRequest) -> ActionResult:
        """Execute the full pipeline for a new action."""

        ctx = PipelineContext(request=request, features=self._features, action_id=str(uuid7()))
        await self.audit.log_action(request, action_id=ctx.action_id)
        return await self._execute_prechecked(ctx, run_gate_checks=True)

    async def execute_approved(self, request: ActionRequest, *, action_id: str, approval_id: str) -> ActionResult:
        """Continue execution after a human approval decision."""

        ctx = PipelineContext(request=request, features=self._features, action_id=action_id, approval_id=approval_id)
        await self.events.publish(
            "approval.continued",
            {"approval_id": approval_id, "action_type": request.action_type},
            action_id=action_id,
            org_id=request.org_id,
        )
        return await self._execute_prechecked(ctx, run_gate_checks=False)

    async def execute_without_persistence(self, request: ActionRequest) -> dict[str, Any]:
        """Minimal fail-open execution path without database writes."""

        action_id = str(uuid7())
        result = await self.tool.execute(request, action_id)
        result["action_id"] = action_id
        return result

    async def _execute_prechecked(self, ctx: PipelineContext, *, run_gate_checks: bool) -> ActionResult:
        request = ctx.request
        assert ctx.action_id is not None

        if self.kg_query is not None and request.resource is not None:
            ctx.kg_context = await self.kg_query.query_context(request.org_id, request.resource.type, request.resource.id)
            await self.events.publish(
                "knowledge.context_loaded",
                {"node_count": len(ctx.kg_context.nodes)},
                action_id=ctx.action_id,
                org_id=request.org_id,
            )

        if run_gate_checks:
            rate_result = await self._check_rate_limit(ctx)
            if rate_result is not None:
                return rate_result

            duplicate_result = await self._check_hard_dedupe(ctx)
            if duplicate_result is not None:
                return duplicate_result

            policy_result = await self._evaluate_policy(ctx)
            if policy_result is not None:
                return policy_result

        await self._score_risk(ctx)

        if run_gate_checks:
            semantic_result = await self._run_semantic_dedupe(ctx)
            if semantic_result is not None:
                return semantic_result

        if request.dry_run:
            return await self._complete(
                ctx,
                status=ActionStatus.DRY_RUN_PASSED,
                reason="Dry run passed; no tool executed",
                result={"dry_run": True},
            )

        if run_gate_checks:
            judge_result = await self._run_judiciary(ctx)
            if judge_result is not None:
                return judge_result

        return await self._execute_delivery(ctx)

    async def _check_rate_limit(self, ctx: PipelineContext) -> ActionResult | None:
        if self.rate_limiter is None:
            return None

        allowed = await self.rate_limiter.check(ctx.request)
        await self.events.publish(
            "rate_limit.evaluated",
            {"allowed": allowed},
            action_id=ctx.action_id,
            org_id=ctx.request.org_id,
        )
        if allowed:
            return None

        return await self._complete(
            ctx,
            status=ActionStatus.BLOCKED,
            reason="Rate limit exceeded",
            result={"blocked_by": "rate_limiter"},
        )

    async def _check_hard_dedupe(self, ctx: PipelineContext) -> ActionResult | None:
        duplicate_of = await self.dedupe_hard.check(ctx.request)
        if duplicate_of is None:
            return None

        ctx.duplicate_of_action_id = duplicate_of
        await self.events.publish(
            "dedupe.hard_matched",
            {"duplicate_of_action_id": duplicate_of},
            action_id=ctx.action_id,
            org_id=ctx.request.org_id,
        )
        return await self._complete(
            ctx,
            status=ActionStatus.BLOCKED,
            reason="Duplicate idempotency key",
            duplicate_of_action_id=duplicate_of,
            result={"blocked_by": "hard_dedupe"},
        )

    async def _evaluate_policy(self, ctx: PipelineContext) -> ActionResult | None:
        policy_result = await self.policy.evaluate(ctx.request)
        await self.events.publish(
            "policy.evaluated",
            {
                "policy_name": policy_result.policy_name,
                "decision": policy_result.decision.value,
                "reason": policy_result.reason,
            },
            action_id=ctx.action_id,
            org_id=ctx.request.org_id,
        )

        if policy_result.decision == PolicyDecision.ALLOW:
            return None
        if policy_result.decision == PolicyDecision.DENY:
            return await self._complete(
                ctx,
                status=ActionStatus.DENIED,
                reason=policy_result.reason or "Denied by policy",
                result={"blocked_by": "policy", "policy_name": policy_result.policy_name},
            )

        if policy_result.decision in {PolicyDecision.REQUIRE_APPROVAL, PolicyDecision.REQUIRE_JUDICIARY}:
            return await self._request_approval(ctx, reason=policy_result.reason or policy_result.decision.value)

        return None

    async def _score_risk(self, ctx: PipelineContext) -> None:
        risk_result = await self.risk.score(ctx.request)
        ctx.risk_score = risk_result.score
        await self.events.publish(
            "risk.scored",
            {"risk_score": risk_result.score, "reason": risk_result.reason},
            action_id=ctx.action_id,
            org_id=ctx.request.org_id,
        )

        async with self._db.session() as session:
            await update_action(session, ctx.action_id, risk_score=risk_result.score)
            await session.commit()

    async def _run_semantic_dedupe(self, ctx: PipelineContext) -> ActionResult | None:
        if self.dedupe_semantic is None:
            return None

        duplicate_of = await self.dedupe_semantic.check(ctx.request)
        if duplicate_of is None:
            return None

        ctx.duplicate_of_action_id = duplicate_of
        await self.events.publish(
            "dedupe.semantic_matched",
            {"duplicate_of_action_id": duplicate_of},
            action_id=ctx.action_id,
            org_id=ctx.request.org_id,
        )
        return await self._complete(
            ctx,
            status=ActionStatus.BLOCKED,
            reason="Semantically similar action detected",
            duplicate_of_action_id=duplicate_of,
            result={"blocked_by": "semantic_dedupe"},
        )

    async def _run_judiciary(self, ctx: PipelineContext) -> ActionResult | None:
        if ctx.risk_score is None:
            return None
        if ctx.risk_score < self._config.pipeline.auto_execute_threshold:
            return None
        if ctx.risk_score >= self._config.pipeline.approval_threshold and self.judiciary is None:
            return await self._request_approval(ctx, reason="Risk score exceeded approval threshold")
        if self.judiciary is None:
            return None

        judge = await self.judiciary.evaluate(ctx.request, ctx.risk_score)
        ctx.judge_score = float(judge["judge_score"])
        await self.events.publish(
            "judiciary.evaluated",
            {"approved": judge["approved"], "reason": judge["reason"], "judge_score": ctx.judge_score},
            action_id=ctx.action_id,
            org_id=ctx.request.org_id,
        )

        async with self._db.session() as session:
            await update_action(session, ctx.action_id, judge_score=ctx.judge_score)
            await session.commit()

        if judge["approved"]:
            return None
        return await self._request_approval(ctx, reason=judge["reason"])

    async def _request_approval(self, ctx: PipelineContext, *, reason: str) -> ActionResult:
        ctx.approval_id = await self.human_approval.request_approval(ctx.request, ctx.action_id)
        await self.events.publish(
            "approval.requested",
            {"approval_id": ctx.approval_id, "reason": reason, "risk_score": ctx.risk_score},
            action_id=ctx.action_id,
            org_id=ctx.request.org_id,
        )
        return await self._complete(
            ctx,
            status=ActionStatus.PENDING_APPROVAL,
            reason=reason,
            result={"approval_id": ctx.approval_id},
            approval_id=ctx.approval_id,
        )

    async def _execute_delivery(self, ctx: PipelineContext) -> ActionResult:
        request = ctx.request

        try:
            if request.resource is not None and self.lock is not None:
                ctx.lock = await self.lock.acquire(request.org_id, request.resource, ctx.action_id)
                if ctx.lock is None:
                    raise ResourceLocked(
                        lock_key=self.lock.build_lock_key(request.resource),
                        locked_by="unknown",
                        retry_after_seconds=self._config.lock.default_ttl_seconds,
                    )
                await self.events.publish(
                    "lock.acquired",
                    {"lock_key": ctx.lock.lock_key, "backend": ctx.lock.backend},
                    action_id=ctx.action_id,
                    org_id=request.org_id,
                )
                ctx.watchdog = LockWatchdog(
                    self.lock,
                    ctx.lock,
                    self._config.lock.default_ttl_seconds * self._config.lock.watchdog_interval_ratio,
                )
                await ctx.watchdog.start()

            if self.circuit_breaker is not None and not await self.circuit_breaker.is_closed(request.action_type):
                return await self._complete(
                    ctx,
                    status=ActionStatus.BLOCKED,
                    reason=f"Circuit breaker open for '{request.action_type}'",
                    result={"blocked_by": "circuit_breaker"},
                )

            started = perf_counter()
            tool_result = await self.tool.execute(request, ctx.action_id)
            ctx.execution_duration_ms = int((perf_counter() - started) * 1000)
            ctx.tool_result = tool_result

            await self._record_tool_call(
                ctx,
                status="executed",
                request_payload=request.payload,
                response_payload=tool_result,
            )
            await self.events.publish(
                "tool.executed",
                {"result": tool_result, "duration_ms": ctx.execution_duration_ms},
                action_id=ctx.action_id,
                org_id=request.org_id,
            )

            if self.circuit_breaker is not None:
                await self.circuit_breaker.record_success(request.action_type)
            if self.reward is not None:
                await self.reward.record_auto(ctx, tool_result)
                if "reward" in tool_result:
                    await self.events.publish(
                        "reward.recorded",
                        {"reward": tool_result["reward"], "source": "auto"},
                        action_id=ctx.action_id,
                        org_id=request.org_id,
                    )
            if self.kg_enricher is not None:
                await self.kg_enricher.update(request.org_id, request, ctx.action_id, tool_result)
                await self.events.publish(
                    "knowledge.enriched",
                    {"resource_type": request.resource.type if request.resource else None},
                    action_id=ctx.action_id,
                    org_id=request.org_id,
                )

            return await self._complete(
                ctx,
                status=ActionStatus.EXECUTED,
                reason=tool_result.get("reason"),
                result=tool_result,
                execution_duration_ms=ctx.execution_duration_ms,
            )
        except ResourceLocked as exc:
            return await self._complete(
                ctx,
                status=ActionStatus.BLOCKED,
                reason=str(exc),
                result={"blocked_by": "resource_lock"},
            )
        except Exception as exc:
            if self.circuit_breaker is not None:
                await self.circuit_breaker.record_failure(request.action_type)
            await self._record_tool_call(
                ctx,
                status="failed",
                request_payload=request.payload,
                response_payload=None,
                error_message=str(exc),
            )
            await self.events.publish(
                "tool.failed",
                {"error": str(exc)},
                action_id=ctx.action_id,
                org_id=request.org_id,
            )
            return await self._complete(
                ctx,
                status=ActionStatus.FAILED,
                reason=str(exc),
                result={"error": str(exc)},
            )
        finally:
            if ctx.watchdog is not None:
                await ctx.watchdog.stop()
            if ctx.lock is not None and self.lock is not None:
                await self.lock.release(ctx.lock)
                await self.events.publish(
                    "lock.released",
                    {"lock_key": ctx.lock.lock_key, "backend": ctx.lock.backend},
                    action_id=ctx.action_id,
                    org_id=request.org_id,
                )

    async def _record_tool_call(
        self,
        ctx: PipelineContext,
        *,
        status: str,
        request_payload: dict[str, Any] | None,
        response_payload: dict[str, Any] | None,
        error_message: str | None = None,
    ) -> None:
        async with self._db.session() as session:
            await create_tool_call(
                session,
                action_id=ctx.action_id,
                org_id=ctx.request.org_id,
                tool_name=ctx.request.action_type,
                request_payload=request_payload,
                response_payload=response_payload,
                status=status,
                latency_ms=ctx.execution_duration_ms,
                error_message=error_message,
            )
            await session.commit()

    async def _complete(
        self,
        ctx: PipelineContext,
        *,
        status: ActionStatus,
        reason: str | None,
        result: dict[str, Any] | None,
        approval_id: str | None = None,
        duplicate_of_action_id: str | None = None,
        execution_duration_ms: int | None = None,
    ) -> ActionResult:
        ctx.final_status = status.value
        ctx.final_reason = reason
        ctx.execution_duration_ms = execution_duration_ms or ctx.execution_duration_ms

        async with self._db.session() as session:
            await update_action(
                session,
                ctx.action_id,
                status=status.value,
                result_payload=result,
                reason=reason,
                risk_score=ctx.risk_score,
                judge_score=ctx.judge_score,
                execution_duration_ms=ctx.execution_duration_ms,
                lock_id=ctx.lock.lock_id if ctx.lock is not None else None,
            )
            await session.commit()

        await self.events.publish(
            "action.completed",
            {"status": status.value, "reason": reason},
            action_id=ctx.action_id,
            org_id=ctx.request.org_id,
        )
        if self.notify is not None:
            await self.notify.send_if_needed(ctx)

        return ActionResult(
            status=status,
            action_id=ctx.action_id,
            result=result,
            reason=reason,
            risk_score=ctx.risk_score,
            judge_score=ctx.judge_score,
            approval_id=approval_id,
            duplicate_of_action_id=duplicate_of_action_id,
            execution_duration_ms=ctx.execution_duration_ms,
        )
