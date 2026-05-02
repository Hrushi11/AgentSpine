"""Workflow performance analysis."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select

from agentspine.db.tables import Action, Reward


class PerformanceAnalyzer:
    def __init__(self, db: Any):
        self._db = db

    async def analyze_workflow(self, workflow_name: str) -> dict[str, Any]:
        async with self._db.session() as session:
            total_actions = await session.scalar(select(func.count()).select_from(Action).where(Action.workflow_id == workflow_name))
            executed_actions = await session.scalar(
                select(func.count()).select_from(Action).where(Action.workflow_id == workflow_name, Action.status == "executed")
            )
            avg_reward = await session.scalar(
                select(func.avg(Reward.reward)).join(Action, Reward.action_id == Action.id).where(Action.workflow_id == workflow_name)
            )

        return {
            "workflow": workflow_name,
            "total_actions": int(total_actions or 0),
            "executed_actions": int(executed_actions or 0),
            "avg_reward": float(avg_reward or 0.0),
        }
