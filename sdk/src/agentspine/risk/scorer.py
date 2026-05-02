"""Risk scoring heuristics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentspine.models import ActionRequest


@dataclass
class RiskResult:
    score: float
    reason: str


class RiskScorer:
    def __init__(self, db: Any):
        self._db = db

    async def score(self, request: ActionRequest) -> RiskResult:
        """Score the risk of an action on a 0.0 to 1.0 scale."""

        score = 0.1
        reasons: list[str] = ["base"]

        action_name = request.action_type.lower()
        destructive_tokens = ["delete", "refund", "terminate", "revoke", "remove"]
        external_tokens = ["send", "notify", "email", "message", "post", "publish"]

        if any(token in action_name for token in destructive_tokens):
            score += 0.45
            reasons.append("destructive_action")

        if any(token in action_name for token in external_tokens):
            score += 0.15
            reasons.append("external_side_effect")

        if request.resource is not None:
            score += 0.1
            reasons.append("resource_targeted")

        if request.context.get("requires_approval") is True:
            score = max(score, 0.75)
            reasons.append("context_requires_approval")

        if request.context.get("sensitive") is True:
            score += 0.2
            reasons.append("sensitive_context")

        if len(request.payload) > 8:
            score += 0.05
            reasons.append("large_payload")

        return RiskResult(score=min(score, 1.0), reason=",".join(reasons))
