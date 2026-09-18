from __future__ import annotations

from typing import Any

from pydantic import Field

from app.domain.events.types import EventSeverity
from app.schemas.common import APIModel


class AlertCreateRequest(APIModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)

    severity: EventSeverity

    agent_id: str | None = None
    session_id: str | None = None
    investigation_id: str | None = None

    detector_id: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class AlertResponse(APIModel):
    alert_id: str
    title: str
    description: str
    severity: EventSeverity
    status: str

    agent_id: str | None = None
    session_id: str | None = None
    investigation_id: str | None = None

    detector_id: str | None = None

    created_at: str
    updated_at: str

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class AlertListResponse(APIModel):
    items: list[AlertResponse] = Field(
        default_factory=list
    )
    page: int
    page_size: int
    total: int
    has_next: bool