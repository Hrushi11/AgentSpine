"""Reward recording and calculation."""

from __future__ import annotations

from typing import Any

from agentspine.db.repository import create_reward
from agentspine.models import RewardInput


class RewardRecorder:
    def __init__(self, db: Any):
        self._db = db

    async def record_auto(self, ctx: Any, result: dict[str, Any]) -> None:
        if not result:
            return
        auto_reward = result.get("reward")
        if auto_reward is None:
            return
        await self.record_manual(ctx.request.org_id, RewardInput(action_id=ctx.action_id, reward=float(auto_reward), source="auto"))

    async def record_manual(self, org_id: str, reward_input: RewardInput) -> None:
        async with self._db.session() as session:
            await create_reward(session, org_id, reward_input)
            await session.commit()
