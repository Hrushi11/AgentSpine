"""Test fixtures."""

import pytest
from typing import AsyncGenerator
from agentspine import AgentSpine, FeatureFlags

@pytest.fixture
async def spine() -> AsyncGenerator[AgentSpine, None]:
    s = AgentSpine(
        workflow="test",
        features=FeatureFlags.minimal()
    )
    yield s
    await s.close()
