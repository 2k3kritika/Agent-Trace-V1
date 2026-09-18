from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from app.domain.events.types import (
    EventRelationshipType,
    EventSeverity,
    EventStatus,
    EventType,
)
from app.schemas.common import APIModel


class EventDetails(APIModel):
    """Flexible event-specific payload."""

    data: dict[str, Any] = Field(
        default_factory=dict
    )


class CanonicalEventCreate(APIModel):
    event_id: str = Field(
        min_length=1,
        max_length=255,
    )

    timestamp: datetime

    session_id: str | None = None
    agent_id: str

    provider: str | None = None

    event_type: EventType
    status: EventStatus = EventStatus.RECEIVED

    tool: str | None = None
    source: str | None = None

    severity: EventSeverity = EventSeverity.LOW

    details: dict[str, Any] = Field(
        default_factory=dict
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    parent_event_id: str | None = None
    related_event_id: str | None = None

    trace_id: str | None = None
    span_id: str | None = None


class CanonicalEventResponse(APIModel):
    id: str
    event_id: str

    timestamp: datetime

    session_id: str | None = None
    agent_id: str

    provider: str | None = None

    event_type: EventType
    status: EventStatus

    tool: str | None = None
    source: str | None = None

    severity: EventSeverity

    details: dict[str, Any] = Field(
        default_factory=dict
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    parent_event_id: str | None = None
    related_event_id: str | None = None

    trace_id: str | None = None
    span_id: str | None = None

    created_at: datetime
    updated_at: datetime


class EventRelationship(APIModel):
    source_event_id: str
    target_event_id: str

    relationship_type: EventRelationshipType


class EventSummary(APIModel):
    event_id: str
    event_type: EventType
    severity: EventSeverity
    status: EventStatus
    timestamp: datetime

    tool: str | None = None
    source: str | None = None


class EventListResponse(APIModel):
    items: list[CanonicalEventResponse]

    page: int
    page_size: int

    total: int
    has_next: bool