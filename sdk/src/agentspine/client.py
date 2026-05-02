"""AgentSpine SDK client — the main entry point."""

from __future__ import annotations

import asyncio
from typing import Any

import structlog

from agentspine.config import ConfigLoader
from agentspine.features import FeatureFlags
from agentspine.models import ActionRequest, ActionResult, Resource

# We will implement these shortly
# from agentspine.db.engine import DatabasePool
# from agentspine.pipeline.orchestrator import PipelineOrchestrator
# from agentspine.lock.redis_backend import RedisPool

logger = structlog.get_logger()


class FailMode:
    """Fail mode determines what happens when the pipeline fails to initialize."""

    CLOSED = "closed"  # Reject all actions if control plane fails
    OPEN = "open"      # Allow all actions if control plane fails (fail-open)


class AgentSpine:
    """Main entry point. Embeds the full control plane pipeline."""

    def __init__(
        self,
        workflow: str,
        *,
        database_url: str | None = None,    # default: env DATABASE_URL
        redis_url: str | None = None,        # default: env REDIS_URL
        config_path: str | None = None,      # path to agentspine.yaml
        secret: str | None = None,           # optional shared secret
        agent: str | None = None,            # default agent name
        features: FeatureFlags | None = None, # feature toggles (default: all on)
        fail_mode: str = FailMode.CLOSED,
    ):
        self._workflow = workflow
        self._default_agent = agent or "default"
        self._features = features or FeatureFlags.full()
        self._config = ConfigLoader.load(config_path, database_url, redis_url)
        self._fail_mode = fail_mode
        self._initialized = False

        # Mocks for now until we build the other modules
        self._db = None
        self._redis = None
        self._pipeline = None

        # Validate: features that require Redis
        if not self._config.redis_url:
            for flag in ["circuit_breaker", "rate_limiter", "distributed_locks"]:
                if getattr(self._features, flag):
                    logger.warning(
                        f"Feature '{flag}' requires Redis but REDIS_URL is not set. "
                        f"Falling back to Postgres or disabling."
                    )

    async def _ensure_init(self) -> None:
        """Lazy initialization — connect pools on first use."""
        if not self._initialized:
            # We will initialize DB/Redis pools and PipelineOrchestrator here
            self._initialized = True

    async def request_action(
        self,
        action_type: str,
        payload: dict[str, Any],
        *,
        agent: str | None = None,
        resource: Resource | None = None,
        context: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        dry_run: bool = False,
    ) -> ActionResult:
        await self._ensure_init()
        request = ActionRequest(
            workflow=self._workflow,
            agent=agent or self._default_agent,
            action_type=action_type,
            payload=payload,
            resource=resource,
            context=context or {},
            idempotency_key=idempotency_key,
            dry_run=dry_run,
        )
        # return await self._pipeline.execute(request)
        # Mock return until pipeline is built
        from agentspine.models import ActionStatus
        return ActionResult(status=ActionStatus.EXECUTED, action_id="mock_id")

    async def publish_event(self, event_type: str, payload: dict[str, Any], **kwargs: Any) -> str:
        """Publish a custom event to the timeline."""
        return "event_id"

    async def record_reward(self, action_id: str, reward: float, **kwargs: Any) -> None:
        """Record a reward signal for an action."""
        pass

    async def configure_workflow(self, name: str, config: dict[str, Any]) -> None:
        """Dynamically configure a workflow."""
        pass

    def agent(self, name: str) -> Any:
        """Decorator to register an agent function."""
        def decorator(fn: Any) -> Any:
            fn._agentspine_agent = name
            return fn
        return decorator

    async def close(self) -> None:
        """Shutdown connection pools."""
        if self._db:
            pass # await self._db.disconnect()
        if self._redis:
            pass # await self._redis.disconnect()

    # Sync wrappers for non-async agents
    def request_action_sync(self, **kwargs: Any) -> ActionResult:
        return asyncio.run(self.request_action(**kwargs))
