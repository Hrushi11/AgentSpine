# AgentSpine V1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the AgentSpine v1 Python SDK and self-hosted control plane described in `agentspine_product_spec.md` and `agentspine_technical_doc.md`, using the current `agentspine/` scaffold as the starting point.

**Architecture:** Monorepo with an embedded Python SDK as the default runtime, an optional FastAPI server for server mode, a Next.js dashboard for approvals and observability, PostgreSQL + pgvector as the source of truth, Redis for locks and limits, and Docker Compose for local/full-stack deployment.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.x, asyncpg, PostgreSQL 16 + pgvector, Redis 7, Pydantic 2, structlog, Alembic, pytest/testcontainers, Next.js 15, Docker Compose.

---

## Scope Boundary

- Build the **v1/MVP** defined by the technical doc and the product doc MVP sections.
- Use a **reference workflow** for validation, but keep the SDK and control plane multipurpose and domain-agnostic.
- Treat the AI SDR / outbound sales flow in the product doc as a **demo wedge**, not as a core architectural dependency.
- Treat these as in-scope for v1:
  - Python SDK
  - action request pipeline
  - generic execution contract for arbitrary tools and action types
  - webhook/signal emission so external services can perform the real side effects
  - generic HTTP/MCP-style adapter surface
  - approval inbox
  - hard dedupe + semantic dedupe
  - basic policy engine
  - LLM judiciary agent
  - reward logging
  - Postgres audit timeline
  - webhook-based notifications/events
  - simple dashboard
- Treat these as **post-v1 backlog**, not blockers for first release:
  - contextual bandits beyond reward logging/scoring
  - offline simulation/replay tooling beyond basic replay
  - TypeScript SDK
  - Helm chart
  - pluggable Kafka/NATS/Redis Streams event bus
  - RBAC/multi-user administration

## Current Scaffold Gaps To Fix First

- `server/` is flat today, but `Makefile`, `docker-compose.dev.yml`, and the technical doc expect `server/src/agentspine_server/...`.
- `dashboard/` is referenced in Compose files but does not exist.
- `migrations/versions/001_initial_schema.py` is empty.
- `sdk/tests/` is expected by `sdk/pyproject.toml` and `Makefile`, but tests currently live at `agentspine/tests/`.
- `README.md` links to `docs/*.md`, but `docs/` is missing.
- Core runtime files still return mocks or `pass`:
  - `sdk/src/agentspine/client.py`
  - `sdk/src/agentspine/pipeline/orchestrator.py`
  - `sdk/src/agentspine/policy/engine.py`
  - `sdk/src/agentspine/risk/scorer.py`
  - `sdk/src/agentspine/tools/executor.py`
  - `sdk/src/agentspine/learning/*`
  - `sdk/src/agentspine/lock/*`
  - `sdk/src/agentspine/vault/*`
  - `sdk/src/agentspine/events/*`
- `docker-compose.yml` and `server/Dockerfile` do not match the target deployment shape from the technical doc.
- Dependency coverage is incomplete versus the technical spec, especially for `redis`, `pgvector`, `prometheus-client`, and optional extras.

## Critical Path

### Phase 0: Normalize Repo Layout And Tooling

- [x] Create `docs/`, `docs/plans/`, and the missing documentation files referenced by `README.md`.
- [x] Normalize the server package to `server/src/agentspine_server/` and replace `server/app.py` with an app factory implementation.
- [x] Decide on one test layout and make the repo consistent:
  - preferred: move tests into `sdk/tests/`
  - alternative: keep root tests and update `Makefile` and `sdk/pyproject.toml`
- [x] Add the missing `dashboard/` app skeleton so Compose stops referencing a nonexistent build context.
- [x] Align `Makefile`, `docker-compose.yml`, `docker-compose.dev.yml`, `server/Dockerfile`, and server import paths to one source of truth.

Verify:
- `docker compose config` succeeds from `agentspine/`
- `python -c "import agentspine"` succeeds in an SDK environment
- `pytest --collect-only` succeeds from the chosen test root

### Phase 1: Finish Packaging, Dependencies, And Environment Setup

- [x] Update `sdk/pyproject.toml` so required runtime dependencies match the technical doc.
- [x] Add missing optional extras for Redis, embeddings, and any server-only packages that should stay out of the SDK core.
- [x] Finalize `server/pyproject.toml` and package metadata so server mode is installable and importable.
- [x] Add dashboard `package.json`, lockfile, and base scripts.
- [x] Make `configs/agentspine.yaml` match the real config schema used by the SDK.

Verify:
- `pip install -e "sdk[dev]"` succeeds
- `pip install -e server/` succeeds
- dashboard dependencies install cleanly

### Phase 2: Implement Database Schema And Persistence Layer

- [x] Finish `sdk/src/agentspine/db/tables.py` so it reflects the v1 data model, including organizations, actions, action events, approvals, rewards, policies, tool calls, KG nodes/edges, semantic fingerprints, locks, credentials, and workflow config.
- [x] Implement `migrations/versions/001_initial_schema.py` from the table definitions and the raw SQL/index requirements in the technical doc.
- [x] Add pgvector extension setup and any custom indexes not expressed declaratively.
- [x] Finalize `sdk/src/agentspine/db/engine.py` connection lifecycle and session helpers.
- [x] Fix or replace raw SQL in `sdk/src/agentspine/db/queries.py` where current parameterization is invalid for intervals/vector casts.

Verify:
- `alembic upgrade head` creates a working schema on a clean Postgres instance
- a smoke test can create an organization, action, and action event row

### Phase 3: Finish SDK Configuration, Models, Exceptions, And Public API

- [x] Complete `sdk/src/agentspine/config.py` so precedence is programmatic > env > YAML > defaults, and all config domains from the technical doc are represented.
- [x] Reconcile `sdk/src/agentspine/models.py` with the technical doc response models, including approval/judiciary metadata and timing fields.
- [x] Expand `sdk/src/agentspine/exceptions.py` to cover SDK, tool, policy, lock, and availability failures cleanly.
- [x] Implement real initialization and teardown in `sdk/src/agentspine/client.py`.
- [x] Ensure `sdk/src/agentspine/__init__.py` exports the intended public API only.

Verify:
- `AgentSpine(...)` can initialize against Postgres/Redis
- invalid config fails early with actionable errors

### Phase 4: Build The Core Action Timeline And Persistence Flow

- [x] Implement event emission/storage for `action.requested`, `policy.evaluated`, `risk.scored`, `lock.acquired`, `approval.requested`, `tool.executed`, `reward.recorded`, and failure events.
- [x] Replace mock `events/logger.py` and `events/stream.py` behavior with append-only DB-backed logging.
- [x] Add persistence helpers for action lifecycle updates, event queries, replay metadata, and tool call logging.
- [x] Ensure every pipeline path writes enough metadata for audit/debugging.

Verify:
- one request creates a full action + event trail in Postgres
- timeline queries can reconstruct execution order

### Phase 5: Implement The Safety Pipeline MVP

- [x] Implement hard dedupe (`dedupe/hard.py`) using idempotency keys and action history.
- [x] Implement policy loading/evaluation using YAML + DB policies in `policy/loader.py`, `policy/engine.py`, `policy/rules.py`, and `policy/provider.py`.
- [x] Implement the initial risk scorer in `risk/scorer.py` using rule/history-based scoring.
- [x] Implement tool registration/execution in `tools/registry.py` and `tools/executor.py`.
- [x] Replace the mock flow in `pipeline/orchestrator.py` with the real fast-path and dry-run behavior.
- [x] Make `client.request_action()` call the real orchestrator and return real `ActionResult` values.

Verify:
- duplicate actions are blocked
- deny policies return `denied`
- low-risk actions execute on the fast path
- dry-run actions do not call real connectors

### Phase 6: Implement Coordination Controls

- [x] Implement Redis lock acquisition/release/renewal plus Postgres advisory lock fallback in `lock/*`.
- [x] Implement the lock watchdog for TTL renewal.
- [x] Implement `ratelimit/limiter.py` as a sliding-window rate limiter.
- [x] Implement `ratelimit/breaker.py` as a per-tool circuit breaker.
- [ ] Map timeouts/retries/tool failures to clear SDK exceptions.

Verify:
- concurrent writes to the same resource serialize correctly
- a noisy tool can be rate-limited and circuit-broken

### Phase 7: Implement Connectors And Real Tool Execution

- [x] Create connector base contracts under `sdk/src/agentspine/tools/connectors/`.
- [x] Implement a generic execution adapter model that supports:
  - local in-process tool execution
  - outbound webhook/event emission
  - generic HTTP execution
  - MCP proxy execution
- [x] Define an outbox/signal contract so a separate app/service can subscribe, decide, and perform the actual side effect against Gmail, CRM, ticketing, or any other downstream system.
- [x] Keep provider-specific integrations out of the core SDK. If needed, add them only as examples or separate optional services.
- [x] Wire credential lookup into connector execution.

Verify:
- the SDK can emit a normalized execution signal for an arbitrary action
- an external worker/service can consume that signal and report the execution result back into AgentSpine
- the same core flow works regardless of downstream system

### Phase 8: Implement Approval, Judiciary, Notifications, And Reward Logging

- [x] Normalize the judiciary package to the technical doc shape:
  - `judiciary/runner.py`
  - provider abstraction
  - rule-based and LLM-based judges
- [x] Implement approval creation, persistence, resolution, and replay/resume semantics.
- [x] Implement notifications through webhook-first dispatch, with Slack/email left as optional example channels.
- [x] Implement reward recording endpoints and SDK entry points.
- [x] Ensure prompt version and model version metadata are recorded on actions.

Verify:
- medium/high-risk actions become `pending_approval`
- human approval or edit resumes execution correctly
- reward records persist and link back to the action

### Phase 9: Implement Knowledge Graph And Semantic Dedupe

- [x] Implement node/edge CRUD and traversal in `knowledge/graph.py`.
- [x] Implement context retrieval in `knowledge/query.py`.
- [x] Implement post-action enrichment in `knowledge/enricher.py`.
- [x] Implement semantic fingerprint generation and similarity lookup in `dedupe/semantic.py` and `dedupe/fingerprint.py`.
- [x] Guard semantic features behind config/feature flags so local minimal mode still works.

Verify:
- semantically similar high-text or high-risk actions can be detected when configured
- KG nodes and edges appear after successful action execution

### Phase 10: Implement Server Mode And Background Workers

- [x] Build the FastAPI app factory and route modules expected by the technical doc:
  - `routes/actions.py`
  - `routes/approvals.py`
  - `routes/events.py`
  - `routes/policies.py`
  - `routes/rewards.py`
  - `routes/workflows.py`
  - `routes/health.py`
- [x] Add `GET /health`, `GET /ready`, and `GET /metrics`.
- [ ] Add async/background workers for judiciary, notifications, and archival/webhook ingestion.
- [x] Add server-mode request handling that forwards to the same pipeline used by the embedded SDK.

Verify:
- `POST /api/v1/actions` works
- readiness checks fail if Postgres/Redis is unavailable
- metrics endpoint exposes Prometheus counters/histograms/gauges

### Phase 11: Build The Dashboard MVP

- [x] Scaffold the Next.js dashboard app and Dockerfile.
- [x] Implement approval inbox UI.
- [x] Implement action timeline UI.
- [x] Implement basic agent/tool performance views.
- [x] Implement policy CRUD screens backed by the server API.
- [ ] Add the dashboard API client and minimal auth/session handling needed for MVP.

Verify:
- a reviewer can view, approve, reject, or edit a pending action from the UI
- the timeline updates after approval/execution

### Phase 12: Finish Observability, Security, Examples, And Documentation

- [ ] Add structured logging context consistently across SDK, server, workers, and connectors.
- [x] Add Prometheus metrics from the technical doc.
- [x] Implement credential vault MVP:
  - environment backend
  - Postgres encrypted backend
  - master-key handling
- [ ] Add example apps and workflows:
  - `examples/quickstart.py`
  - generic human-in-the-loop workflow
  - external executor/outbox consumer example
  - customer support flow
  - custom connector/adapter example
  - custom policy example
- [x] Write the missing docs referenced by `README.md`:
  - `docs/quickstart.md`
  - `docs/architecture.md`
  - `docs/deployment.md`
  - `docs/plugins.md`
  - `docs/api-reference.md`

Verify:
- local quickstart works from documented steps
- docs match the actual file layout and commands

### Phase 13: Build The Full Test Pyramid And Release Pipeline

- [x] Add unit tests for policy, dedupe, risk, config, locks, limits, and circuit breaker.
- [ ] Add integration tests using testcontainers for Postgres + Redis.
- [ ] Add E2E tests for the full approval flow, duplicate blocking, and reward ingestion.
- [ ] Add load/performance smoke coverage for latency and connection pool behavior.
- [x] Add CI for lint, type-check, tests, migrations, package build, and Docker builds.
- [x] Add package/release automation for the SDK.

Verify:
- `ruff check`, `ruff format --check`, `mypy`, and `pytest` all pass
- `docker compose up -d` starts the full stack cleanly
- package build completes

## Parallel Workstreams After Phase 3

- **Workstream A: Pipeline backend**
  - phases 4, 5, 6, 7, 8, 9
- **Workstream B: Server/API**
  - phase 10 once SDK persistence contracts stabilize
- **Workstream C: Dashboard/frontend**
  - phase 11 once API contracts for approvals/timeline/policies stabilize
- **Workstream D: DevEx and docs**
  - phase 12 can start once repo layout is normalized
- **Workstream E: QA and release**
  - phase 13 starts in parallel as soon as phase 4 has real behavior to test

## Recommended MVP Demo Acceptance Criteria

- [x] Any workflow agent can call `AgentSpine.request_action(...)` for an arbitrary action type without the SDK assuming a specific provider or vertical.
- [x] Hard dedupe blocks the same idempotency key.
- [x] Semantic dedupe detects materially similar high-text or high-risk actions when configured.
- [x] Policy rules can deny or require approval.
- [x] Judiciary scoring can route actions into fast path vs approval path.
- [ ] A human can approve/edit/reject from the dashboard.
- [x] External execution signals are logged with a full action timeline.
- [x] Webhook notifications are emitted for approval-required, failed, or execution-ready actions.
- [x] Customer reply or webhook can record a reward against the action.
- [x] Observability surfaces action counts, failures, latencies, and pending approvals.

## Post-V1 Backlog

- [ ] Adaptive learning phase 2: historical reward scoring and prompt version quality ranking.
- [ ] Adaptive learning phase 3: contextual bandits for prompt/action selection.
- [ ] Adaptive learning phase 4: offline simulation and judge comparison workflows.
- [ ] Platform features: plugin interface maturity, vault adapters, advanced policy operators, richer webhook ingestion and outbox consumers.
- [ ] Community/scale features: TypeScript SDK, Helm chart, HA guidance, event-bus adapters, RBAC.

## Done When

- [ ] The embedded SDK path works end-to-end for a general multipurpose reference workflow, with downstream execution handled through the generic adapter/signal boundary.
- [ ] The optional server mode works with the same core pipeline contracts.
- [x] The dashboard supports approval inbox, timeline, and basic policy/insight workflows.
- [ ] The full stack can be started from Docker Compose and exercised using documented examples.
- [ ] Tests, packaging, docs, and release automation are in place for a public v1 release.
