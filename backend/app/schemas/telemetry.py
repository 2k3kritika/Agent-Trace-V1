"""
Telemetry ingestion schemas.

Telemetry represents provider/application input before it is necessarily
normalized into the canonical AgentTrace event model.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.schemas.common import APIModel, FlexibleAPIModel
from app.schemas.events import CanonicalEventCreate
from pydantic import Field, field_validator


class TelemetryEventRequest(FlexibleAPIModel):
    """
    Provider-neutral telemetry ingestion payload.

    The payload deliberately permits additional provider-specific fields.
    Adapters are responsible for interpreting those fields.
    """

    event_id: str | None = Field(default=None, max_length=128)
    timestamp: datetime | None = None

    session_id: str = Field(min_length=1, max_length=128)
    agent_id: str = Field(min_length=1, max_length=128)
    provider: str = Field(min_length=1, max_length=128)

    event_type: str = Field(min_length=1, max_length=128)
    status: str = Field(min_length=1, max_length=64)

    tool: str | None = Field(default=None, max_length=255)
    source: str | None = Field(default=None, max_length=255)
    severity: str | None = Field(default=None, max_length=32)

    details: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    parent_event_id: str | None = Field(default=None, max_length=128)
    related_event_id: str | None = Field(default=None, max_length=128)

    trace_id: str | None = Field(default=None, max_length=128)
    span_id: str | None = Field(default=None, max_length=128)

    @field_validator(
        "event_type",
        "status",
        "severity",
        mode="before",
    )
    @classmethod
    def normalize_strings(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip().upper()

        return value


class TelemetryBatchRequest(APIModel):
    """Batch telemetry ingestion request."""

    events: list[TelemetryEventRequest] = Field(
        min_length=1,
        max_length=1000,
    )


class TelemetryIngestResponse(APIModel):
    """Result returned after telemetry ingestion."""

    event_id: str
    accepted: bool
    normalized: bool
    message: str


class TelemetryBatchResponse(APIModel):
    """Result returned after batch ingestion."""

    accepted: int = Field(ge=0)
    rejected: int = Field(ge=0)
    event_ids: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class TelemetrySessionRequest(APIModel):
    """Request for creating/registering a telemetry session."""

    session_id: str = Field(min_length=1, max_length=128)
    agent_id: str = Field(min_length=1, max_length=128)
    provider: str = Field(min_length=1, max_length=128)

    started_at: datetime | None = None
    scenario: str | None = Field(default=None, max_length=255)

    metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizedTelemetry(APIModel):
    """
    Internal representation produced by the normalization pipeline.

    It intentionally contains a canonical event rather than duplicating
    provider-specific fields.
    """

    canonical_event: CanonicalEventCreate
    adapter_name: str
    normalized_at: datetime
