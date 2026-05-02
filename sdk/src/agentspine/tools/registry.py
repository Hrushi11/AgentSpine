"""Tool registry to manage available tools."""

class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name: str, func: callable) -> None:
        self._tools[name] = func

    def get(self, name: str) -> callable:
        return self._tools.get(name)
