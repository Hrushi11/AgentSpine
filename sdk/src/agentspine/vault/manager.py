"""Credential vault facade."""

from __future__ import annotations

from typing import Any


class CredentialVault:
    def __init__(self, backend: Any):
        self._backend = backend

    async def get_credentials(self, org_id: str, tool_name: str) -> dict[str, Any]:
        return await self._backend.get_credentials(org_id, tool_name)

    async def store_credentials(self, org_id: str, tool_name: str, data: dict[str, Any]) -> None:
        await self._backend.store_credentials(org_id, tool_name, data)
