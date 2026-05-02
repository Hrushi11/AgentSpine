.PHONY: dev test lint type-check migrate format clean docker-up docker-down

# ============================================================
# Development
# ============================================================

dev: docker-up migrate  ## Start infra + run migrations
	@echo "Infrastructure ready. Install SDK: cd sdk && pip install -e '.[dev]'"

docker-up:  ## Start Postgres + Redis
	docker compose up -d postgres redis

docker-down:  ## Stop all containers
	docker compose down

# ============================================================
# SDK
# ============================================================

install:  ## Install SDK in dev mode
	cd sdk && pip install -e ".[dev]"

test:  ## Run all tests
	cd sdk && pytest tests/ -v --tb=short

test-unit:  ## Run unit tests only
	cd sdk && pytest tests/unit/ -v --tb=short

test-integration:  ## Run integration tests (requires Docker)
	cd sdk && pytest tests/integration/ -v --tb=short

test-e2e:  ## Run end-to-end tests (requires Docker)
	cd sdk && pytest tests/e2e/ -v --tb=short

lint:  ## Run linter
	cd sdk && ruff check src/ tests/

format:  ## Format code
	cd sdk && ruff format src/ tests/

type-check:  ## Run type checker
	cd sdk && mypy src/

# ============================================================
# Database
# ============================================================

migrate:  ## Run database migrations
	alembic -c migrations/alembic.ini upgrade head

migrate-new:  ## Create a new migration (usage: make migrate-new MSG="add foo table")
	alembic -c migrations/alembic.ini revision --autogenerate -m "$(MSG)"

migrate-rollback:  ## Rollback last migration
	alembic -c migrations/alembic.ini downgrade -1

migrate-status:  ## Show migration status
	alembic -c migrations/alembic.ini current

# ============================================================
# Server
# ============================================================

server:  ## Start the FastAPI server
	cd server && uvicorn agentspine_server.app:create_app --factory --host 0.0.0.0 --port 8080 --reload

# ============================================================
# Docker (full stack)
# ============================================================

stack-up:  ## Start full stack (Postgres + Redis + Server + Dashboard)
	docker compose up -d

stack-down:  ## Stop full stack
	docker compose down -v

stack-logs:  ## Tail logs for all services
	docker compose logs -f

# ============================================================
# Clean
# ============================================================

clean:  ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf sdk/dist/ server/dist/

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
