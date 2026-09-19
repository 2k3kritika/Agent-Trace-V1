from __future__ import annotations

import base64

from app.core.exceptions import AppError
from app.infrastructure.storage.local import (
    LocalArtifactStorage,
)
from app.schemas.artifacts import (
    ArtifactCreateRequest,
    ArtifactResponse,
)


class ArtifactService:
    def __init__(
        self,
        storage: LocalArtifactStorage,
    ):
        self.storage = storage

    async def create_artifact(
        self,
        request: ArtifactCreateRequest,
    ) -> ArtifactResponse:
        if request.content is None:
            raise AppError(
                status_code=400,
                message="Artifact content is required.",
            )

        try:
            content = base64.b64decode(
                request.content,
                validate=True,
            )
        except Exception as exc:
            raise AppError(
                status_code=400,
                message=("Artifact content must be valid base64 data."),
            ) from exc

        stored = await self.storage.store(
            filename=request.filename,
            content=content,
            content_type=request.content_type,
        )

        return ArtifactResponse(
            artifact_id=stored.artifact_id,
            investigation_id=request.investigation_id,
            evidence_id=request.evidence_id,
            artifact_type=request.artifact_type,
            filename=stored.filename,
            content_type=stored.content_type,
            size_bytes=stored.size_bytes,
            storage_uri=stored.storage_uri,
            sha256=stored.sha256,
            metadata=request.metadata,
            created_at=stored.created_at,
        )

    async def read_artifact(
        self,
        storage_uri: str,
    ) -> bytes:
        try:
            return await self.storage.read(storage_uri)
        except FileNotFoundError as exc:
            raise AppError(
                status_code=404,
                message="Artifact was not found.",
            ) from exc

    async def delete_artifact(
        self,
        storage_uri: str,
    ) -> None:
        await self.storage.delete(storage_uri)
