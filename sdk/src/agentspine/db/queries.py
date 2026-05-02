"""Raw SQL queries optimized for low latency."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def check_semantic_duplicate(
    session: AsyncSession,
    org_id: str,
    action_type: str,
    embedding: list[float],
    lookback_days: int = 7,
    threshold: float = 0.92,
) -> str | None:
    """Use pgvector to find similar recent actions using cosine distance (<=>).
    Distance = 1 - cosine_similarity. So similarity > 0.92 means distance < 0.08.
    """
    stmt = text("""
        SELECT action_id, (1 - (intent_embedding <=> :embedding::vector)) as similarity
        FROM semantic_fingerprints
        WHERE organization_id = :org_id
          AND action_type = :action_type
          AND created_at >= now() - interval ':days days'
          AND (1 - (intent_embedding <=> :embedding::vector)) > :threshold
        ORDER BY intent_embedding <=> :embedding::vector
        LIMIT 1
    """)
    result = await session.execute(
        stmt,
        {
            "org_id": org_id,
            "action_type": action_type,
            "embedding": embedding,
            "days": lookback_days,
            "threshold": threshold,
        },
    )
    row = result.first()
    return row.action_id if row else None


async def try_acquire_advisory_lock(session: AsyncSession, lock_id: int) -> bool:
    """Postgres advisory lock (session level). Returns True if acquired."""
    stmt = text("SELECT pg_try_advisory_lock(:lock_id)")
    result = await session.execute(stmt, {"lock_id": lock_id})
    return result.scalar() is True


async def release_advisory_lock(session: AsyncSession, lock_id: int) -> bool:
    """Release a session-level advisory lock."""
    stmt = text("SELECT pg_advisory_unlock(:lock_id)")
    result = await session.execute(stmt, {"lock_id": lock_id})
    return result.scalar() is True
