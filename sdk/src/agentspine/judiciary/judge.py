"""Heuristic judiciary evaluation for high-risk actions."""

from __future__ import annotations

from typing import Any

from agentspine.config import Config
from agentspine.models import ActionRequest


class AIJudge:
    def __init__(self, db: Any, config: Config):
        self._db = db
        self._config = config

    async def evaluate(self, request: ActionRequest, risk_score: float) -> dict[str, Any]:
        approved = risk_score < self._config.approval_threshold
        reason = "approved_by_heuristic_judge" if approved else "escalate_to_human"
        judge_score = max(0.0, 1.0 - risk_score)
        return {"approved": approved, "reason": reason, "judge_score": judge_score}
