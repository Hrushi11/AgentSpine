---
title: Configuration
description: Detailed guide on configuring the AgentSpine SDK.
---

AgentSpine uses a robust, 4-tier configuration system that ensures flexibility across different environments (local development, staging, and production).

## Configuration Priority

Settings are resolved in the following order (Highest to Lowest):

1. **Programmatic**: Passed directly to the `AgentSpine` constructor.
2. **Environment Variables**: System-level variables prefixed with `AGENTSPINE_`.
3. **YAML File**: Configuration defined in an `agentspine.yaml` file.
4. **Internal Defaults**: Built-in defaults (e.g., `localhost:5432` for Postgres).

---

## 1. Programmatic Configuration

Ideal for dynamic environments or when using secret managers (AWS Secrets Manager, Vault).

```python
from agentspine import AgentSpine, AgentSpineConfig
from agentspine.config import DatabaseConfig, RedisConfig

config = AgentSpineConfig(
    database=DatabaseConfig(
        url="postgresql+asyncpg://user:pass@db.example.com:5432/spine"
    ),
    redis=RedisConfig(
        url="redis://cache.example.com:6379/0"
    )
)

spine = AgentSpine(workflow="production_bot", config=config)
```

## 2. Environment Variables

Standard for containerized deployments (Docker, Kubernetes).

| Variable | Description | Default |
| :--- | :--- | :--- |
| `AGENTSPINE_DATABASE_URL` | Async Postgres connection string | `postgresql+asyncpg://...` |
| `AGENTSPINE_REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `AGENTSPINE_LOG_LEVEL` | Logging level (DEBUG, INFO, etc.) | `INFO` |
| `AGENTSPINE_CONFIG_PATH` | Custom path to the YAML config file | `./agentspine.yaml` |

## 3. YAML Configuration

Drop an `agentspine.yaml` file in your project root for easy local management.

```yaml
# agentspine.yaml
database:
  url: "postgresql+asyncpg://user:pass@localhost:5432/agentspine"
  pool_size: 20

redis:
  url: "redis://localhost:6379/0"
  timeout: 5.0

logging:
  level: "DEBUG"
  format: "json"
```

## Advanced Settings

### Feature Flags
You can enable or disable specific AgentSpine features globally:

```yaml
features:
  deduplication: true
  policy_enforcement: true
  vault_integration: false
```
