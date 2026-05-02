"""Environment variable credential store."""

from __future__ import annotations

import json
import os
from typing import Any


class EnvVaultBackend:
    async def get_credentials(self, org_id: str, tool_name: str) -> dict[str, Any]:
        key = f"AGENTSPINE_CREDENTIALS_{org_id}_{tool_name}".upper().replace("-", "_").replace(".", "_")
        payload = os.environ.get(key, "")
        if not payload:
            return {}
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return {}

    async def store_credentials(self, org_id: str, tool_name: str, data: dict[str, Any]) -> None:
        raise NotImplementedError("EnvVaultBackend is read-only")
