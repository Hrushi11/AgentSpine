"""Pipeline step aliases for backwards-compatible imports."""

from agentspine.dedupe.hard import HardDeduper as HardDedupeStep
from agentspine.dedupe.semantic import SemanticDeduper as SemanticDedupeStep
from agentspine.events.stream import EventStream as EventStep
from agentspine.judiciary.runner import JudiciaryRunner as JudiciaryStep
from agentspine.knowledge.enricher import KnowledgeEnricher as KnowledgeGraphStep
from agentspine.learning.reward import RewardRecorder as RewardStep
from agentspine.lock.manager import LockManager as LockStep
from agentspine.notify.router import NotificationRouter as NotifyStep
from agentspine.policy.engine import PolicyEngine as PolicyStep
from agentspine.ratelimit.breaker import CircuitBreaker
from agentspine.ratelimit.limiter import RateLimiter
from agentspine.risk.scorer import RiskScorer as RiskStep
from agentspine.tools.executor import ToolExecutor as ToolExecutorStep

__all__ = [
    "HardDedupeStep",
    "SemanticDedupeStep",
    "EventStep",
    "JudiciaryStep",
    "KnowledgeGraphStep",
    "RewardStep",
    "LockStep",
    "NotifyStep",
    "PolicyStep",
    "CircuitBreaker",
    "RateLimiter",
    "RiskStep",
    "ToolExecutorStep",
]
