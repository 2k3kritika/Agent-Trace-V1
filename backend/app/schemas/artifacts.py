from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.common import APIModel


class ArtifactCreateRequest(APIModel):
    investigation_id: str | None = None
    evidence_id: str | None = None
    artifact_type: str
    filename: str
    content_type: str = "application/octet-stream"
    content: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactUploadRequest(APIModel):
    filename: str
    content_type: str = "application/octet-stream"
    content_base64: str
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


class ArtifactUploadResponse(APIModel):
    artifact_uri: str
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactContentResponse(APIModel):
    artifact_uri: str
    content_type: str
    content_base64: str
    size_bytes: int
    filename: str | None = None


class ArtifactDeleteResponse(APIModel):
    deleted: bool
    artifact_uri: str


class ArtifactListResponse(APIModel):
    items: list[ArtifactResponse]
    page: int
    page_size: int
    total: int
    has_next: bool