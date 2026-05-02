"""Environment variable credential store."""

import os
from typing import Any

class EnvVaultBackend:
    async def get_credentials(self, org_id: str, tool_name: str) -> dict[str, Any]:
        """Load from environment variables."""
        return {}

    async def store_credentials(self, org_id: str, tool_name: str, data: dict[str, Any]) -> None:
        raise NotImplementedError("EnvVaultBackend is read-only")
