"""Configuration loading — env vars, YAML files, programmatic overrides."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
import structlog

logger = structlog.get_logger()


@dataclass
class DatabaseConfig:
    url: str = ""
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
    ) -> Config:
        config = Config()

        # Layer 1: YAML file
        yaml_path = config_path or os.environ.get("AGENTSPINE_CONFIG_PATH")
        if yaml_path and Path(yaml_path).exists():
            ConfigLoader._apply_yaml(config, yaml_path)

        # Layer 2: Environment variables
        ConfigLoader._apply_env(config)

        # Layer 3: Programmatic overrides (highest priority)
        if database_url:
            config.database.url = database_url
        if redis_url:
            config.redis.url = redis_url

        # Validate required config
        if not config.database.url:
            raise ValueError(
                "DATABASE_URL is required. Set it via env var, agentspine.yaml, "
                "or the database_url constructor parameter."
            )

        return config

    @staticmethod
    def _apply_yaml(config: Config, path: str) -> None:
        with open(path) as f:
            data: dict[str, Any] = yaml.safe_load(f) or {}

        if "database" in data:
            for k, v in data["database"].items():
                if hasattr(config.database, k):
                    setattr(config.database, k, v)

        if "redis" in data:
            for k, v in data["redis"].items():
                if hasattr(config.redis, k):
                    setattr(config.redis, k, v)

        if "pipeline" in data:
            for k, v in data["pipeline"].items():
                if hasattr(config.pipeline, k):
                    setattr(config.pipeline, k, v)

        if "dedupe" in data:
            for k, v in data["dedupe"].items():
                if hasattr(config.dedupe, k):
                    setattr(config.dedupe, k, v)

        if "embedding" in data:
            for k, v in data["embedding"].items():
                if hasattr(config.embedding, k):
                    setattr(config.embedding, k, v)

        if "lock" in data:
            for k, v in data["lock"].items():
                if hasattr(config.lock, k):
                    setattr(config.lock, k, v)

        if "graph" in data:
            for k, v in data["graph"].items():
                if hasattr(config.graph, k):
                    setattr(config.graph, k, v)

        logger.info("config.loaded_yaml", path=path)

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
