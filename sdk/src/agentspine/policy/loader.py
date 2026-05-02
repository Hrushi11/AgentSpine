"""Load policies from DB or YAML."""

from typing import Any

class PolicyLoader:
    def __init__(self, db: Any):
        self._db = db

    async def load_all(self) -> list[Any]:
        return []
