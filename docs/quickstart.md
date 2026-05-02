# Quickstart

AgentSpine is an embedded Python SDK with an optional server mode and dashboard.

## Local SDK Development

```bash
cd agentspine
docker compose up -d postgres redis
cd sdk
pip install -e ".[dev]"
```

Use the SDK from source:

```bash
set PYTHONPATH=src
python ..\examples\quickstart.py
```

To test the generic external execution boundary, point `AGENTSPINE_EXECUTION_WEBHOOK_URL` at the reference worker:

```bash
python ..\examples\external_executor.py
```

## Local Full Stack

```bash
cd agentspine
docker compose up -d
```

Services:

- `postgres` on `5432`
- `redis` on `6379`
- `server` on `8080`
- `dashboard` on `3000`

## Configuration

Primary configuration sources:

1. Constructor arguments
2. Environment variables
3. `configs/agentspine.yaml`

Important variables:

- `DATABASE_URL`
- `REDIS_URL`
- `AGENTSPINE_CONFIG_PATH`
- `AGENTSPINE_LOG_LEVEL`
- `AGENTSPINE_LOG_FORMAT`
