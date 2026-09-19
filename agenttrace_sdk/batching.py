from __future__ import annotations

from agenttrace_sdk.client import AgentTraceClient
from agenttrace_sdk.models import SDKEvent


class EventBatcher:
    """
    Lightweight in-memory telemetry batcher.

    The batcher is deliberately simple for the local MVP. It does not spawn
    background threads or silently lose events during interpreter shutdown.
    """

    def __init__(
        self,
        client: AgentTraceClient,
        max_size: int = 20,
    ) -> None:
        if max_size < 1:
            raise ValueError("max_size must be greater than zero.")

        self.client = client
        self.max_size = max_size
        self._events: list[SDKEvent] = []

    @property
    def size(self) -> int:
        return len(self._events)

    def add(self, event: SDKEvent) -> dict | None:
        self._events.append(event)

        if len(self._events) >= self.max_size:
            return self.flush()

        return None

    def emit(
        self,
        event_type: str,
        **kwargs,
    ) -> dict | None:
        event = self.client._build_event(
            event_type,
            **kwargs,
        )

        return self.add(event)

    def flush(self) -> dict | None:
        if not self._events:
            return None

        events = self._events
        self._events = []

        return self.client.emit_batch(events)

    def clear(self) -> None:
        self._events.clear()