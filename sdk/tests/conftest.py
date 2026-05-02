"""Test fixtures for the SDK test suite."""

from collections.abc import AsyncGenerator

import pytest

from agentspine import AgentSpine, FeatureFlags


@pytest.fixture
async def spine() -> AsyncGenerator[AgentSpine, None]:
    s = AgentSpine(
        workflow="test",
        features=FeatureFlags.minimal(),
    )
    yield s
    await s.close()
