from datetime import datetime
from typing import Any

from app.schemas.common import APIModel
from pydantic import Field


class ArtifactCreateRequest(APIModel):
    investigation_id: str | None = None
    evidence_id: str | None = None
    artifact_type: str
    filename: str
    content_type: str = "application/octet-stream"
    content: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactResponse(APIModel):
    artifact_id: str
    investigation_id: str | None = None
    evidence_id: str | None = None

    artifact_type: str
    filename: str
    content_type: str

    size_bytes: int
    storage_uri: str

    sha256: str

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime


class ArtifactListResponse(APIModel):
    items: list[ArtifactResponse]
    page: int
    page_size: int
    total: int
    has_next: bool
