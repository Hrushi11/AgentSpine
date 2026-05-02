"""Configuration loading for AgentSpine."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog
import yaml

logger = structlog.get_logger()
ENV_PATTERN = re.compile(r"^\$\{(?P<name>[A-Z0-9_]+)(:-\"?(?P<default>.*)\"?)?\}$")

DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/agentspine"


@dataclass
class DatabaseConfig:
    url: str = DEFAULT_DATABASE_URL
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class RedisConfig:
    url: str = ""


@dataclass
class PipelineConfig:
    auto_execute_threshold: float = 0.25
    approval_threshold: float = 0.50
    timeout_per_step_ms: int = 5000
    judiciary_timeout_ms: int = 30000


@dataclass
class DedupeConfig:
    semantic_enabled: bool = True
    similarity_threshold: float = 0.92
    lookback_days: int = 7


@dataclass
class EmbeddingConfig:
    model: str = "all-MiniLM-L6-v2"


@dataclass
class LockConfig:
    default_ttl_seconds: int = 300
    watchdog_interval_ratio: float = 0.33
    backend: str = "redis"


@dataclass
class GraphConfig:
    backend: str = "postgres"
    cache_ttl_seconds: int = 300
    max_traversal_depth: int = 4


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    window_seconds: int = 60
    recovery_seconds: int = 30


@dataclass
class RateLimitConfig:
    window_seconds: int = 60
    max_requests_per_agent: int = 200
    max_requests_per_workflow: int = 1000


@dataclass
class NotificationConfig:
    execution_webhook_url: str = ""
    approval_webhook_url: str = ""
    failure_webhook_url: str = ""


@dataclass
class SecurityConfig:
    master_key: str = ""


@dataclass
class LoggingConfig:
    level: str = "info"
    format: str = "json"


@dataclass
class Config:
    """Merged configuration from all sources."""

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    dedupe: DedupeConfig = field(default_factory=DedupeConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    lock: LockConfig = field(default_factory=LockConfig)
    graph: GraphConfig = field(default_factory=GraphConfig)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @property
    def database_url(self) -> str:
        return self.database.url

    @property
    def redis_url(self) -> str:
        return self.redis.url

    @property
    def auto_execute_threshold(self) -> float:
        return self.pipeline.auto_execute_threshold

    @property
    def approval_threshold(self) -> float:
        return self.pipeline.approval_threshold


class ConfigLoader:
    """Load configuration with priority: programmatic > env > yaml > defaults."""

    @staticmethod
    def load(
        config_path: str | None = None,
        database_url: str | None = None,
        redis_url: str | None = None,
        secret: str | None = None,
    ) -> Config:
        config = Config()

        yaml_path = config_path or os.environ.get("AGENTSPINE_CONFIG_PATH")
        if yaml_path and Path(yaml_path).exists():
            ConfigLoader._apply_yaml(config, yaml_path)

        ConfigLoader._apply_env(config)

        if database_url:
            config.database.url = database_url
        if redis_url:
            config.redis.url = redis_url
        if secret:
            config.security.master_key = secret

        if not config.database.url:
            config.database.url = DEFAULT_DATABASE_URL

        return config

    @staticmethod
    def _apply_yaml(config: Config, path: str) -> None:
        with open(path, encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f) or {}

        ConfigLoader._apply_mapping(config, data)
        logger.info("config.loaded_yaml", path=path)

    @staticmethod
    def _apply_mapping(config: Config, data: dict[str, Any]) -> None:
        normalized = ConfigLoader._resolve_placeholders(data)
        mapping = {
            "database": config.database,
            "redis": config.redis,
            "pipeline": config.pipeline,
            "dedupe": config.dedupe,
            "embedding": config.embedding,
            "lock": config.lock,
            "graph": config.graph,
            "circuit_breaker": config.circuit_breaker,
            "rate_limit": config.rate_limit,
            "notifications": config.notifications,
            "security": config.security,
            "logging": config.logging,
        }

        for key, target in mapping.items():
            if key in normalized and isinstance(normalized[key], dict):
                for field_name, value in normalized[key].items():
                    if hasattr(target, field_name):
                        setattr(target, field_name, value)

        if "auto_execute_threshold" in normalized:
            config.pipeline.auto_execute_threshold = normalized["auto_execute_threshold"]
        if "approval_threshold" in normalized:
            config.pipeline.approval_threshold = normalized["approval_threshold"]

    @staticmethod
    def _apply_env(config: Config) -> None:
        if url := os.environ.get("DATABASE_URL"):
            config.database.url = url
        if url := os.environ.get("REDIS_URL"):
            config.redis.url = url
        if level := os.environ.get("AGENTSPINE_LOG_LEVEL"):
            config.logging.level = level
        if fmt := os.environ.get("AGENTSPINE_LOG_FORMAT"):
            config.logging.format = fmt
        if model := os.environ.get("AGENTSPINE_EMBEDDING_MODEL"):
            config.embedding.model = model
        if secret := os.environ.get("AGENTSPINE_MASTER_KEY"):
            config.security.master_key = secret
        if webhook := os.environ.get("AGENTSPINE_EXECUTION_WEBHOOK_URL"):
            config.notifications.execution_webhook_url = webhook
        if webhook := os.environ.get("AGENTSPINE_APPROVAL_WEBHOOK_URL"):
            config.notifications.approval_webhook_url = webhook
        if webhook := os.environ.get("AGENTSPINE_FAILURE_WEBHOOK_URL"):
            config.notifications.failure_webhook_url = webhook

    @staticmethod
    def _resolve_placeholders(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: ConfigLoader._resolve_placeholders(item) for key, item in value.items()}
        if isinstance(value, list):
            return [ConfigLoader._resolve_placeholders(item) for item in value]
        if not isinstance(value, str):
            return value

        match = ENV_PATTERN.match(value.strip())
        if match is None:
            return value

        env_name = match.group("name")
        default = match.group("default") or ""
        return os.environ.get(env_name, default.strip('"'))
