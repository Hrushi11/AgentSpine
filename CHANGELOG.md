# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project scaffold
- SDK core: client, config, models, exceptions, feature flags
- Pipeline orchestrator with feature-flagged steps
- Policy engine with DB-backed rules
- Semantic deduplication via pgvector
- Distributed lock manager (Redis + Postgres fallback)
- Knowledge graph (Postgres backend, pluggable)
- Credential vault (AES-256 encryption)
- Rate limiter and circuit breaker
- Event timeline (append-only audit log)
- Tool executor with connector registry
- Notification dispatcher (Slack, email, webhook)
- Judiciary system (LLM + rule-based judges)
- Learning engine (rewards, contextual bandit)
- FastAPI server for dashboard and webhooks
- Alembic migrations for initial schema
- Docker Compose for full-stack deployment
