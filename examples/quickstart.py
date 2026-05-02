"""Minimal embedded SDK example."""

from __future__ import annotations

import asyncio

from agentspine import AgentSpine


async def main() -> None:
    spine = AgentSpine(workflow="quickstart")

    async def local_echo(payload, context):
        return {"echo": payload, "context_keys": sorted(context.keys())}

    spine.register_tool("demo.echo", local_echo)

    result = await spine.request_action(
        action_type="demo.echo",
        payload={"text": "hello"},
        idempotency_key="quickstart-001",
    )
    print(result.model_dump(mode="json"))
    await spine.close()


if __name__ == "__main__":
    asyncio.run(main())
