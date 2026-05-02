"""Retry utilities with jitter."""

import asyncio
import random
from typing import Callable, Any

async def with_retry(func: Callable, max_retries: int = 3, base_delay: float = 1.0) -> Any:
    """Execute with exponential backoff and jitter."""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            await asyncio.sleep(delay)
