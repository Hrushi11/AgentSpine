"""Built-in policy rule evaluation."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from agentspine.db.tables import Policy
from agentspine.models import ActionRequest, PolicyDecision


class RuleEvaluator:
    """Evaluate simple JSON policy conditions against an action request."""

    def matches(self, policy: Policy, request: ActionRequest) -> bool:
        condition = policy.condition or {}

        return all(
            [
                self._match_values(request.action_type, condition.get("action_types")),
                self._match_values(request.workflow, condition.get("workflows")),
                self._match_values(request.agent, condition.get("agents")),
                self._match_values(request.resource.type if request.resource else None, condition.get("resource_types")),
                self._match_values(request.resource.id if request.resource else None, condition.get("resource_ids")),
                self._match_dict(request.payload, condition.get("payload_equals")),
                self._match_dict(request.context, condition.get("context_equals")),
                self._match_dict_contains(request.payload, condition.get("payload_contains")),
                self._match_dict_contains(request.context, condition.get("context_contains")),
            ]
        )

    def normalize_decision(self, action: str) -> PolicyDecision:
        value = action.lower().strip()
        mapping = {
            "allow": PolicyDecision.ALLOW,
            "deny": PolicyDecision.DENY,
            "require_approval": PolicyDecision.REQUIRE_APPROVAL,
            "require_human_approval": PolicyDecision.REQUIRE_APPROVAL,
            "require_judiciary": PolicyDecision.REQUIRE_JUDICIARY,
            "require_judiciary_agent": PolicyDecision.REQUIRE_JUDICIARY,
        }
        return mapping.get(value, PolicyDecision.ALLOW)

    @staticmethod
    def _match_values(actual: str | None, expected: Any) -> bool:
        if expected is None:
            return True
        if isinstance(expected, str):
            return actual == expected
        if isinstance(expected, Iterable):
            return actual in expected
        return False

    @staticmethod
    def _match_dict(actual: dict[str, Any], expected: Any) -> bool:
        if expected is None:
            return True
        if not isinstance(expected, dict):
            return False
        return all(actual.get(key) == value for key, value in expected.items())

    @staticmethod
    def _match_dict_contains(actual: dict[str, Any], expected: Any) -> bool:
        if expected is None:
            return True
        if not isinstance(expected, dict):
            return False

        for key, value in expected.items():
            candidate = actual.get(key)
            if isinstance(candidate, str) and isinstance(value, str):
                if value.lower() not in candidate.lower():
                    return False
            elif candidate != value:
                return False
        return True
