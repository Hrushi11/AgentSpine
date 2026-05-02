"""Judiciary runner abstraction."""

from __future__ import annotations

from typing import Any

from agentspine.config import Config
from agentspine.judiciary.judge import AIJudge
from agentspine.models import ActionRequest


class JudiciaryRunner:
    def __init__(self, db: Any, config: Config):
        self._judge = AIJudge(db, config)

    async def evaluate(self, request: ActionRequest, risk_score: float) -> dict[str, Any]:
        return await self._judge.evaluate(request, risk_score)
