from datetime import datetime
from typing import Any

from app.schemas.common import APIModel, PageResponse
from pydantic import Field


class EvidenceCreateRequest(APIModel):
    investigation_id: str
    event_id: str | None = None
    evidence_type: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    storage_uri: str | None = None
    sha256: str | None = Field(default=None, max_length=64)
    content: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceUpdateRequest(APIModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    storage_uri: str | None = None
    sha256: str | None = Field(default=None, max_length=64)
    content: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class EvidenceResponse(APIModel):
    evidence_id: str
    investigation_id: str
    event_id: str | None
    evidence_type: str
    title: str
    description: str | None
    storage_uri: str | None
    sha256: str | None
    content: dict[str, Any] | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class EvidenceListResponse(PageResponse[EvidenceResponse]):
    pass
