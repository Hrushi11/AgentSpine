---
title: Deployment
description: Deploying AgentSpine in production environments.
---

AgentSpine is designed to be highly portable, whether you are running it as an embedded SDK or a centralized server.

## Infrastructure Requirements

For a production deployment, you need:
- **PostgreSQL 16+**: Source of truth for executions, events, and policies.
- **Redis 7+**: Used for distributed locks, idempotency keys, and coordination.

## Deployment Patterns

### 1. Embedded SDK (Python)
In this mode, AgentSpine runs inside your application process. Deployment simply involves:
- Installing the `agentspine` package.
- Setting `AGENTSPINE_DATABASE_URL` and `AGENTSPINE_REDIS_URL` in your environment.

### 2. Centralized Server (Full Stack)
The centralized server provides a REST API and handles the Dashboard.

#### Using Docker Compose
The easiest way to deploy the full stack is using our reference `docker-compose.yml`:

```bash
docker compose up -d
```

This starts:
- **Postgres**: State store.
- **Redis**: Caching/Idempotency.
- **AgentSpine Server**: The control plane API.
- **AgentSpine Dashboard**: The UI at `http://localhost:3000`.

## Production Checklist

- [ ] **Database Backups**: Ensure regular backups of the Postgres instance.
- [ ] **Redis Persistence**: Enable AOF or RDB persistence in Redis to avoid losing idempotency state.
- [ ] **Security**: Secure your database and Redis ports. Use `AGENTSPINE_MASTER_KEY` for sensitive data encryption.
- [ ] **Observability**: Monitor the `/health` and `/metrics` endpoints.
