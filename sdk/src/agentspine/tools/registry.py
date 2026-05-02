"""Tool registry for local and external execution adapters."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

ToolCallable = Callable[[dict[str, Any], dict[str, Any]], Awaitable[dict[str, Any]] | dict[str, Any]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolCallable] = {}
        self._prefix_tools: dict[str, ToolCallable] = {}

    def register(self, name: str, func: ToolCallable) -> None:
        self._tools[name] = func

    def register_prefix(self, prefix: str, func: ToolCallable) -> None:
        self._prefix_tools[prefix] = func

    def get(self, name: str) -> ToolCallable | None:
        if name in self._tools:
            return self._tools[name]

        for prefix, func in self._prefix_tools.items():
            if name.startswith(prefix):
                return func

        return None
