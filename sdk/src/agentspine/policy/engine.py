"""Policy evaluation engine."""

from __future__ import annotations

from time import monotonic
from typing import Any

from agentspine.config import Config
from agentspine.models import ActionRequest, PolicyDecision, PolicyResult
from agentspine.policy.loader import PolicyLoader
from agentspine.policy.provider import PolicyProvider
from agentspine.policy.rules import RuleEvaluator


class PolicyEngine:
    """Evaluates policies against an action request."""

    def __init__(self, db: Any, config: Config):
        self._db = db
        self._loader = PolicyLoader(db)
        self._cache: list[Any] = []
        self._cache_ttl = 60.0
        self._last_refresh = 0.0
        self._custom_providers: list[PolicyProvider] = []
        self._rules = RuleEvaluator()

    def register_provider(self, provider: PolicyProvider) -> None:
        self._custom_providers.append(provider)

    async def evaluate(self, request: ActionRequest) -> PolicyResult:
        for provider in self._custom_providers:
            result = await provider.evaluate(request)
            if result is not None:
                return result

        await self._refresh_cache_if_needed(request.org_id)

        for policy in self._cache:
            if self._rules.matches(policy, request):
                return PolicyResult(
                    policy_name=policy.name,
                    decision=self._rules.normalize_decision(policy.action),
                    reason=f"Matched policy '{policy.name}'",
                )

        return PolicyResult(
            policy_name="default",
            decision=PolicyDecision.ALLOW,
            reason="No matching policy",
        )

    async def _refresh_cache_if_needed(self, org_id: str) -> None:
        now = monotonic()
        if now - self._last_refresh < self._cache_ttl and self._cache:
            return

        self._cache = await self._loader.load_all(org_id)
        self._last_refresh = now
