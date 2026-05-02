# Deployment

## Local Docker Compose

Use `docker-compose.yml` for the full stack and `docker-compose.dev.yml` for local development overrides.

Core services:

- PostgreSQL with pgvector
- Redis
- FastAPI server
- Next.js dashboard

## Environment

Required:

- `DATABASE_URL`

Optional:

- `REDIS_URL`
- `AGENTSPINE_CONFIG_PATH`
- `AGENTSPINE_MASTER_KEY`

## Deployment Shape

The target deployment shape is:

1. Postgres as source of truth
2. Redis for locks and runtime coordination
3. AgentSpine server for HTTP mode and dashboard APIs
4. External executor services that consume webhook or outbox signals

## Notes

- `server/` now builds from the normalized `src/agentspine_server/` package layout.
- The dashboard expects the API at `NEXT_PUBLIC_API_URL` in the browser and `AGENTSPINE_API_URL` for server-side fetches.
- The reference stack is intentionally generic: downstream Gmail, CRM, ticketing, or messaging integrations should live in separate executor services.
