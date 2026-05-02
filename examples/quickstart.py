"""AgentSpine Quickstart Example."""

import asyncio
from agentspine import AgentSpine, FeatureFlags

async def main():
    # Initialize the spine with minimal features for testing
    spine = AgentSpine(
        workflow="demo",
        features=FeatureFlags.minimal()
    )

    # Request an action
    result = await spine.request_action(
        action_type="send_email",
        payload={"to": "user@example.com", "subject": "Hello"},
        agent="demo_agent",
        dry_run=True  # Safely run the pipeline
    )

    print(f"Action Result: {result.status}")
    if result.reason:
        print(f"Reason: {result.reason}")

    await spine.close()

if __name__ == "__main__":
    asyncio.run(main())
