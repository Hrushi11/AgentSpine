"""Parallel execution utilities for the pipeline."""

import asyncio
from typing import Any, Awaitable

async def execute_parallel(*tasks: Awaitable[Any]) -> tuple[Any, ...]:
    """Execute multiple awaitables in parallel and return their results."""
    return await asyncio.gather(*tasks, return_exceptions=True)
