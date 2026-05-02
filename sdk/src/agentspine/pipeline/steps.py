"""Individual pipeline step definitions."""

from typing import Any

class HardDedupeStep:
    def __init__(self, db: Any):
        self.db = db

class PolicyStep:
    def __init__(self, db: Any, config: Any):
        self.db = db
        self.config = config

class RiskStep:
    def __init__(self, db: Any):
        self.db = db

class ToolExecutorStep:
    def __init__(self, db: Any, config: Any):
        self.db = db
        self.config = config

class EventStep:
    def __init__(self, db: Any):
        self.db = db

class SemanticDedupeStep:
    def __init__(self, db: Any):
        self.db = db

class KnowledgeGraphStep:
    def __init__(self, db: Any, config: Any):
        self.db = db
        self.config = config

class LockStep:
    def __init__(self, redis: Any, db: Any):
        self.redis = redis
        self.db = db

class JudiciaryStep:
    def __init__(self, db: Any, config: Any):
        self.db = db
        self.config = config

class RewardStep:
    def __init__(self, db: Any):
        self.db = db

class NotifyStep:
    def __init__(self, config: Any):
        self.config = config

class RateLimiter:
    def __init__(self, redis: Any, db: Any, config: Any):
        self.redis = redis
        self.db = db
        self.config = config

class CircuitBreaker:
    def __init__(self, redis: Any, config: Any):
        self.redis = redis
        self.config = config

# --- NoOp Stubs (zero overhead when features are disabled) ---

class NoOpDedupeStep:
    async def check(self, request: Any) -> Any: return None

class NoOpKGStep:
    async def query_context(self, request: Any) -> Any: return None
    async def update(self, ctx: Any, request: Any, result: Any) -> None: pass

class NoOpLockStep:
    async def acquire(self, resource: Any, action_id: Any) -> Any: return None
    async def release(self, lock: Any) -> None: pass

class NoOpRewardStep:
    async def record_auto(self, ctx: Any, result: Any) -> None: pass

class NoOpNotifyStep:
    async def send_if_needed(self, ctx: Any) -> None: pass

class NoOpRateLimiter:
    async def check(self, request: Any) -> bool: return True

class NoOpCircuitBreaker:
    async def is_closed(self, tool_name: Any) -> bool: return True
