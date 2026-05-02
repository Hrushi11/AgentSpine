"""Risk scoring."""

from typing import Any
from dataclasses import dataclass

from agentspine.models import ActionRequest

@dataclass
class RiskResult:
    score: float
    reason: str

class RiskScorer:
    def __init__(self, db: Any):
        self._db = db

    async def score(self, request: ActionRequest) -> RiskResult:
        """Score the risk of an action (0.0 to 1.0)."""
        return RiskResult(score=0.1, reason="Default scaffold score")
