from datetime import datetime
from typing import Any

from app.schemas.common import APIModel
from pydantic import Field


class ReportCreateRequest(APIModel):
    investigation_id: str
    report_type: str = "FORENSIC"
    title: str | None = None


class ReportUpdateRequest(APIModel):
    status: str | None = None
    title: str | None = None
    content: str | None = None
    storage_uri: str | None = None
    metadata: dict[str, Any] | None = None


class ReportResponse(APIModel):
    id: str
    investigation_id: str
    report_type: str
    status: str
    title: str
    content: str | None = None
    storage_uri: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ReportListResponse(APIModel):
    items: list[ReportResponse]
    page: int
    page_size: int
    total: int
    has_next: bool
