from __future__ import annotations

from datetime import datetime
from typing import Any

from app.schemas.common import APIModel
from pydantic import Field


class AgentCreateRequest(APIModel):
    agent_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    provider: str = Field(min_length=1, max_length=100)

    description: str | None = None
    provider_display_name: str | None = None
    integration_type: str | None = None

    capabilities: dict[str, Any] = Field(default_factory=dict)


class AgentUpdateRiskRequest(APIModel):
    risk_score: int = Field(
        ge=0,
        le=100,
    )
    risk_level: str = Field(
        min_length=1,
        max_length=50,
    )


class AgentResponse(APIModel):
    id: str
    agent_id: str
    name: str
    description: str | None = None
    provider: str
    provider_display_name: str | None = None

    status: str
    risk_score: int
    risk_level: str

    last_seen: datetime | None = None

    integration_type: str | None = None

    capabilities: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime
    updated_at: datetime


class AgentListResponse(APIModel):
    items: list[AgentResponse]
    page: int
    page_size: int
    total: int
    has_next: bool
