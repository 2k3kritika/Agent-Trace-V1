from __future__ import annotations

from app.core.exceptions import AppError
from app.schemas.artifacts import (
    ArtifactContentResponse,
    ArtifactDeleteResponse,
    ArtifactUploadRequest,
    ArtifactUploadResponse,
)
from app.services.storage_service import StorageService


class ArtifactService:
    def __init__(self, storage_service: StorageService) -> None:
        self.storage_service = storage_service

    async def upload(
        self,
        request: ArtifactUploadRequest,
    ) -> ArtifactUploadResponse:
        try:
            result = await self.storage_service.save_base64(
                filename=request.filename,
                content_type=request.content_type,
                content_base64=request.content_base64,
                metadata=request.metadata,
            )
        except ValueError as exc:
            raise AppError(
                status_code=400,
                message=str(exc),
            ) from exc

        return ArtifactUploadResponse.model_validate(result)

    async def get_content(
        self,
        artifact_uri: str,
    ) -> ArtifactContentResponse:
        try:
            result = await self.storage_service.get(artifact_uri)
        except FileNotFoundError as exc:
            raise AppError(
                status_code=404,
                message="Artifact not found.",
            ) from exc
        except ValueError as exc:
            raise AppError(
                status_code=400,
                message=str(exc),
            ) from exc

        return ArtifactContentResponse.model_validate(result)

    async def delete(
        self,
        artifact_uri: str,
    ) -> ArtifactDeleteResponse:
        try:
            deleted = await self.storage_service.delete(artifact_uri)
        except FileNotFoundError as exc:
            raise AppError(
                status_code=404,
                message="Artifact not found.",
            ) from exc
        except ValueError as exc:
            raise AppError(
                status_code=400,
                message=str(exc),
            ) from exc

        return ArtifactDeleteResponse(
            deleted=deleted,
            artifact_uri=artifact_uri,
        )
