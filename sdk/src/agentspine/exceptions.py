"""AgentSpine exception hierarchy."""

from __future__ import annotations


class AgentSpineError(Exception):
    """Base exception for all AgentSpine errors."""


class AgentSpineTimeout(AgentSpineError):
    """A pipeline step exceeded its timeout."""


class AgentSpineUnavailable(AgentSpineError):
    """Database or Redis connection failed."""


class ResourceLocked(AgentSpineError):
    """Resource is locked by another action."""

    def __init__(self, lock_key: str, locked_by: str, retry_after_seconds: int) -> None:
        self.lock_key = lock_key
        self.locked_by = locked_by
        self.retry_after_seconds = retry_after_seconds
        super().__init__(
            f"Resource '{lock_key}' is locked by '{locked_by}'. "
            f"Retry after {retry_after_seconds}s."
        )


class ToolNotFound(AgentSpineError):
    """No connector registered for the action type."""


class ToolTimeout(AgentSpineError):
    """Tool execution exceeded its timeout."""


class ToolExecutionError(AgentSpineError):
    """Tool connector raised an error during execution."""

    def __init__(self, tool_name: str, detail: str) -> None:
        self.tool_name = tool_name
        self.detail = detail
        super().__init__(f"Tool '{tool_name}' failed: {detail}")


class CredentialNotFound(AgentSpineError):
    """No credentials found for the tool."""


class PolicyViolation(AgentSpineError):
    """Action was denied by the policy engine."""
