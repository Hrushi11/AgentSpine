"""Reward recording and calculation."""

from typing import Any

class RewardRecorder:
    def __init__(self, db: Any):
        self._db = db

    async def record_auto(self, ctx: Any, result: dict[str, Any]) -> None:
        pass

    async def record_manual(self, action_id: str, reward: float, source: str) -> None:
        pass
