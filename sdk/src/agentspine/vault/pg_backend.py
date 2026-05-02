"""Postgres encrypted credential store."""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

from cryptography.fernet import Fernet
from sqlalchemy import select

from agentspine.db.tables import ToolCredential


class PostgresVaultBackend:
    def __init__(self, db: Any, secret: str):
        self._db = db
        self._fernet = Fernet(self._build_key(secret))

    async def get_credentials(self, org_id: str, tool_name: str) -> dict[str, Any]:
        async with self._db.session() as session:
            result = await session.execute(
                select(ToolCredential).where(
                    ToolCredential.organization_id == org_id,
                    ToolCredential.tool_name == tool_name,
                )
            )
            row = result.scalar_one_or_none()
            if row is None:
                return {}
            decrypted = self._fernet.decrypt(bytes(row.encrypted_data))
            return json.loads(decrypted.decode("utf-8"))

    async def store_credentials(self, org_id: str, tool_name: str, data: dict[str, Any]) -> None:
        payload = self._fernet.encrypt(json.dumps(data).encode("utf-8"))
        async with self._db.session() as session:
            result = await session.execute(
                select(ToolCredential).where(
                    ToolCredential.organization_id == org_id,
                    ToolCredential.tool_name == tool_name,
                )
            )
            row = result.scalar_one_or_none()
            if row is None:
                row = ToolCredential(organization_id=org_id, tool_name=tool_name, encrypted_data=payload)
                session.add(row)
            else:
                row.encrypted_data = payload
            await session.commit()

    @staticmethod
    def _build_key(secret: str) -> bytes:
        digest = hashlib.sha256(secret.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)
