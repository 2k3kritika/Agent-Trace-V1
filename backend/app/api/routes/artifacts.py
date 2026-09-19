from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.schemas.artifacts import (
    ArtifactCreateRequest,
    ArtifactResponse,
)
from app.services.artifact_service import ArtifactService
from app.services.dependency import (
    get_artifact_service,
)

router = APIRouter(
    prefix="/artifacts",
    tags=["Artifacts"],
)


@router.post(
    "",
    response_model=ArtifactResponse,
)
async def create_artifact(
    request: ArtifactCreateRequest,
    service: ArtifactService = Depends(
        get_artifact_service
    ),
) -> ArtifactResponse:
    return await service.create_artifact(
        request
    )


@router.get(
    "/content",
)
async def read_artifact(
    storage_uri: str,
    service: ArtifactService = Depends(
        get_artifact_service
    ),
) -> Response:
    content = await service.read_artifact(
        storage_uri
    )

    return Response(
        content=content,
        media_type="application/octet-stream",
    )


@router.delete(
    "/content",
)
async def delete_artifact(
    storage_uri: str,
    service: ArtifactService = Depends(
        get_artifact_service
    ),
) -> dict[str, str]:
    await service.delete_artifact(
        storage_uri
    )

    return {
        "message": "Artifact deleted successfully."
    }