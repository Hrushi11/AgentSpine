"""Feature flags for toggling pipeline subsystems."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FeatureFlags:
    """Toggle individual pipeline subsystems on/off.

    Every flag defaults to True for a batteries-included experience.
    Users can disable features they don't need to reduce latency,
    memory, and infrastructure requirements.

    Core features (policy engine, event timeline) are always on
    and cannot be disabled.
    """

    # --- Optional features (can be toggled) ---
    semantic_dedupe: bool = True       # requires: pgvector extension, sentence-transformers
    knowledge_graph: bool = True       # requires: kg_nodes/kg_edges tables
    circuit_breaker: bool = True       # requires: Redis
    rate_limiter: bool = True          # requires: Redis
    distributed_locks: bool = True     # requires: Redis (fallback: Postgres advisory locks)
    judiciary: bool = True             # requires: judge provider registration
    rewards: bool = True               # reward ingestion + learning loop
    notifications: bool = True         # Slack/email/webhook notifications
    credential_vault: bool = True      # encrypted credential storage

    @classmethod
    def minimal(cls) -> FeatureFlags:
        """Minimal mode: policy + events only. Lowest overhead."""
        return cls(
            semantic_dedupe=False,
            knowledge_graph=False,
            circuit_breaker=False,
            rate_limiter=False,
            distributed_locks=False,
            judiciary=False,
            rewards=False,
            notifications=False,
            credential_vault=False,
        )

    @classmethod
    def standard(cls) -> FeatureFlags:
        """Standard mode: everything except KG and judiciary."""
        return cls(
            knowledge_graph=False,
            judiciary=False,
        )

    @classmethod
    def full(cls) -> FeatureFlags:
        """Full mode: all features enabled (default)."""
        return cls()
