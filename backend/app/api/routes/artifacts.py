from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.schemas.artifacts import (
    ArtifactContentResponse,
    ArtifactDeleteResponse,
    ArtifactUploadRequest,
    ArtifactUploadResponse,
)
from app.services.artifact_service import ArtifactService
from app.services.dependency import get_artifact_service


router = APIRouter(
    prefix="/artifacts",
    tags=["Artifacts"],
)


@router.post(
    "",
    response_model=ArtifactUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_artifact(
    request: ArtifactUploadRequest,
    service: ArtifactService = Depends(get_artifact_service),
) -> ArtifactUploadResponse:
    return await service.upload(request)


@router.get(
    "/content",
    response_model=ArtifactContentResponse,
)
async def get_artifact_content(
    artifact_uri: str = Query(..., min_length=1),
    service: ArtifactService = Depends(get_artifact_service),
) -> ArtifactContentResponse:
    return await service.get_content(artifact_uri)


@router.delete(
    "/content",
    response_model=ArtifactDeleteResponse,
)
async def delete_artifact_content(
    artifact_uri: str = Query(..., min_length=1),
    service: ArtifactService = Depends(get_artifact_service),
) -> ArtifactDeleteResponse:
    return await service.delete(artifact_uri)