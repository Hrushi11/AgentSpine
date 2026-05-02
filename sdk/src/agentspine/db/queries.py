"""Raw SQL helpers for AgentSpine."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def try_acquire_advisory_lock(session: AsyncSession, lock_id: int) -> bool:
    """Postgres advisory lock (session level)."""

    result = await session.execute(text("SELECT pg_try_advisory_lock(:lock_id)"), {"lock_id": lock_id})
    return result.scalar() is True


async def release_advisory_lock(session: AsyncSession, lock_id: int) -> bool:
    """Release a session-level advisory lock."""

    result = await session.execute(text("SELECT pg_advisory_unlock(:lock_id)"), {"lock_id": lock_id})
    return result.scalar() is True
