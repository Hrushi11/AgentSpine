# Contributing to AgentSpine

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone the repo
git clone https://github.com/org/agentspine
cd agentspine

# Start infrastructure
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Install SDK in dev mode
cd sdk
pip install -e ".[dev]"

# Run migrations
cd ..
alembic upgrade head

# Run tests
pytest sdk/tests/ -v
```

## Code Style

- **Formatter/Linter**: `ruff` (replaces black, isort, flake8)
- **Type Checking**: `mypy --strict`
- **Test Framework**: `pytest` with `pytest-asyncio`

```bash
ruff check sdk/
ruff format sdk/
mypy sdk/src/
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Ensure linting passes (`ruff check .`)
6. Submit a pull request

## Architecture

See [docs/architecture.md](docs/architecture.md) for the system design.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
