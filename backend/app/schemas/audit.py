from __future__ import annotations

from datetime import datetime
from typing import Any

from app.schemas.common import APIModel
from pydantic import Field


class AuditLogRequest(APIModel):
    action: str = Field(
        min_length=1,
        max_length=120,
    )

    resource_type: str = Field(
        min_length=1,
        max_length=80,
    )

    resource_id: str | None = Field(
        default=None,
        max_length=120,
    )

    description: str = Field(
        min_length=1,
        max_length=1000,
    )

    severity: str = "LOW"

    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditLogResponse(APIModel):
    audit_id: str
    timestamp: datetime

    actor_user_id: str | None
    actor_email: str | None
    actor_role: str | None

    action: str
    resource_type: str
    resource_id: str | None

    description: str
    severity: str

    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditLogListResponse(APIModel):
    items: list[AuditLogResponse]
    page: int
    page_size: int
    total: int
    has_next: bool
