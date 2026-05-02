from pathlib import Path

from agentspine.config import ConfigLoader


CONFIG_PATH = Path(__file__).resolve().parents[3] / "configs" / "agentspine.yaml"


def test_config_loader_resolves_env_placeholders(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")
    config = ConfigLoader.load(str(CONFIG_PATH))
    assert config.database.url == "postgresql+asyncpg://test:test@localhost:5432/testdb"


def test_config_loader_uses_defaults_when_env_missing(monkeypatch):
    monkeypatch.delenv("AGENTSPINE_MASTER_KEY", raising=False)
    config = ConfigLoader.load(str(CONFIG_PATH))
    assert config.security.master_key == "dev-only-master-key"
