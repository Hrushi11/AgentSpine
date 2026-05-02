"""Event stream abstraction (Kafka, Redis Streams, or raw PG)."""

from typing import Any

class EventStream:
    def __init__(self, backend: Any):
        self._backend = backend

    async def publish(self, event_type: str, payload: dict[str, Any]) -> str:
        return "mock_event_id"
