from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.common import APIModel


class IntegrationCreateRequest(APIModel):
    agent_id: str = Field(
        min_length=1,
        max_length=255,
    )

    integration_type: str = Field(
        min_length=1,
        max_length=100,
    )

    provider: str = Field(
        min_length=1,
        max_length=100,
    )

    endpoint: str | None = None

    api_key_reference: str | None = Field(
        default=None,
        max_length=255,
    )

    environment: str | None = Field(
        default=None,
        max_length=100,
    )

    status: str = Field(
        default="active",
        max_length=50,
    )

    configuration: dict[str, Any] = Field(
        default_factory=dict
    )


class IntegrationUpdateRequest(APIModel):
    endpoint: str | None = None

    environment: str | None = Field(
        default=None,
        max_length=100,
    )

    status: str | None = Field(
        default=None,
        max_length=50,
    )

    configuration: dict[str, Any] | None = None


class IntegrationResponse(APIModel):
    id: str
    agent_id: str

    integration_type: str
    provider: str

    endpoint: str | None = None
    api_key_reference: str | None = None
    environment: str | None = None

    status: str

    configuration: dict[str, Any] = Field(
        default_factory=dict
    )

    created_at: datetime
    updated_at: datetime


class IntegrationListResponse(APIModel):
    items: list[IntegrationResponse]
    page: int
    page_size: int
    total: int
    has_next: bool