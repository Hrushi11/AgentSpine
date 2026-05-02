"""Lock watchdog for TTL renewal."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import Any


class LockWatchdog:
    def __init__(self, manager: Any, lock: Any, interval_seconds: float):
        self._manager = manager
        self._lock = lock
        self._interval_seconds = interval_seconds
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        with suppress(asyncio.CancelledError):
            await self._task
        self._task = None

    async def _run(self) -> None:
        while True:
            await asyncio.sleep(self._interval_seconds)
            renewed = await self._manager.renew(self._lock)
            if not renewed:
                return
