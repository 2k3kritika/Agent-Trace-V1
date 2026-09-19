from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.exceptions import DuplicateResourceError, NotFoundError
from app.schemas.integrations import (
    IntegrationCreateRequest,
    IntegrationListResponse,
    IntegrationResponse,
    IntegrationUpdateRequest,
)
from app.services.dependency import (
    get_integration_service,
)
from app.services.integration_service import (
    IntegrationService,
)

router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
)


def _to_response(integration) -> IntegrationResponse:
    return IntegrationResponse.model_validate(
        integration,
        from_attributes=True,
    )


@router.post(
    "",
    response_model=IntegrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_integration(
    request: IntegrationCreateRequest,
    service: IntegrationService = Depends(get_integration_service),
) -> IntegrationResponse:
    try:
        integration = await service.create_integration(
            agent_id=request.agent_id,
            integration_type=request.integration_type,
            provider=request.provider,
            endpoint=request.endpoint,
            api_key_reference=(request.api_key_reference),
            environment=request.environment,
            status=request.status,
            configuration=request.configuration,
        )

        return _to_response(integration)

    except DuplicateResourceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=IntegrationListResponse,
)
async def list_integrations(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=25,
        ge=1,
        le=100,
    ),
    agent_id: str | None = None,
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    provider: str | None = None,
    integration_type: str | None = None,
    service: IntegrationService = Depends(get_integration_service),
) -> IntegrationListResponse:
    result = await service.list_integrations(
        page=page,
        page_size=page_size,
        agent_id=agent_id,
        status=status_filter,
        provider=provider,
        integration_type=integration_type,
    )

    return IntegrationListResponse(
        items=[_to_response(item) for item in result.items],
        page=page,
        page_size=page_size,
        total=result.total,
        has_next=(page * page_size < result.total),
    )


@router.get(
    "/{integration_id}",
    response_model=IntegrationResponse,
)
async def get_integration(
    integration_id: str,
    service: IntegrationService = Depends(get_integration_service),
) -> IntegrationResponse:
    try:
        integration = await service.get_integration(integration_id)

        return _to_response(integration)

    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{integration_id}",
    response_model=IntegrationResponse,
)
async def update_integration(
    integration_id: str,
    request: IntegrationUpdateRequest,
    service: IntegrationService = Depends(get_integration_service),
) -> IntegrationResponse:
    try:
        integration = await service.update_integration(
            integration_id,
            status=request.status,
            endpoint=request.endpoint,
            environment=request.environment,
            configuration=request.configuration,
        )

        return _to_response(integration)

    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{integration_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_integration(
    integration_id: str,
    service: IntegrationService = Depends(get_integration_service),
) -> None:
    try:
        await service.delete_integration(integration_id)

    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
