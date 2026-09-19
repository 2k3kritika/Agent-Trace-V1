from __future__ import annotations

from datetime import datetime
from typing import Any

from app.schemas.common import APIModel
from pydantic import Field


class SessionCreateRequest(APIModel):
    session_id: str = Field(
        min_length=1,
        max_length=255,
    )

    agent_id: str = Field(
        min_length=1,
        max_length=255,
    )

    provider: str | None = Field(
        default=None,
        max_length=100,
    )

    scenario: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionResponse(APIModel):
    id: str
    session_id: str
    agent_id: str
    provider: str | None = None

    status: str

    started_at: datetime
    ended_at: datetime | None = None
    duration: int | None = None

    event_count: int
    alert_count: int

    risk_score: int
    risk_level: str

    scenario: str | None = None

    investigation_id: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime
    updated_at: datetime


class SessionListResponse(APIModel):
    items: list[SessionResponse]
    page: int
    page_size: int
    total: int
    has_next: bool
