from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class SDKEvent(BaseModel):
    """
    Provider-neutral event emitted by an AgentTrace-instrumented agent.
    """

    event_id: str | None = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    agent_id: str
    session_id: str | None = None

    provider: str = "local"
    event_type: str
    status: str = "RECEIVED"

    tool: str | None = None
    source: str = "agenttrace_sdk"
    severity: str | None = None

    details: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    parent_event_id: str | None = None
    related_event_id: str | None = None

    trace_id: str | None = None
    span_id: str | None = None

    def as_payload(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json")

        if payload.get("event_id") is None:
            payload.pop("event_id", None)

        return payload


class SDKBatch(BaseModel):
    events: list[SDKEvent] = Field(default_factory=list)

    def as_payload(self) -> dict[str, Any]:
        return {
            "events": [
                event.as_payload()
                for event in self.events
            ]
        }