"""Example of creating a policy through the SDK."""

from __future__ import annotations

import asyncio

from agentspine import AgentSpine


async def main() -> None:
    spine = AgentSpine(workflow="policy-demo")
    await spine.save_policy(
        org_id="default",
        name="require-approval-for-refunds",
        action="require_approval",
        condition={"action_types": ["billing.refund"]},
        scope_type="workflow",
        scope_id="policy-demo",
        priority=100,
    )
    print("policy saved")
    await spine.close()


if __name__ == "__main__":
    asyncio.run(main())
