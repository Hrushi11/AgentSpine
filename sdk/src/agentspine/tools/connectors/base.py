"""Provider-agnostic execution connector contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ConnectorContext:
    action_id: str
    org_id: str
    workflow: str
    agent: str
    action_type: str
    payload: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)
    credentials: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConnectorResult:
    status: str
    payload: dict[str, Any] = field(default_factory=dict)


class ExecutionConnector(Protocol):
    async def execute(self, ctx: ConnectorContext) -> ConnectorResult:
        """Execute a normalized action request."""
