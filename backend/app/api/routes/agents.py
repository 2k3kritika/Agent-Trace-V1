from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.exceptions import DuplicateResourceError, NotFoundError
from app.schemas.agents import (
    AgentCreateRequest,
    AgentListResponse,
    AgentResponse,
    AgentUpdateRiskRequest,
)
from app.services.agent_service import AgentService
from app.services.dependency import get_agent_service

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


def _to_response(agent) -> AgentResponse:
    return AgentResponse.model_validate(
        agent,
        from_attributes=True,
    )


@router.post(
    "",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_agent(
    request: AgentCreateRequest,
    service: AgentService = Depends(get_agent_service),
) -> AgentResponse:
    try:
        agent = await service.register_agent(
            agent_id=request.agent_id,
            name=request.name,
            provider=request.provider,
            description=request.description,
            provider_display_name=(request.provider_display_name),
            integration_type=request.integration_type,
            capabilities=request.capabilities,
        )

        return _to_response(agent)

    except DuplicateResourceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=AgentListResponse,
)
async def list_agents(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=25,
        ge=1,
        le=100,
    ),
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    provider: str | None = None,
    risk_level: str | None = None,
    search: str | None = None,
    service: AgentService = Depends(get_agent_service),
) -> AgentListResponse:
    result = await service.list_agents(
        page=page,
        page_size=page_size,
        status=status_filter,
        provider=provider,
        risk_level=risk_level,
        search=search,
    )

    return AgentListResponse(
        items=[_to_response(agent) for agent in result.items],
        page=page,
        page_size=page_size,
        total=result.total,
        has_next=(page * page_size < result.total),
    )


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
)
async def get_agent(
    agent_id: str,
    service: AgentService = Depends(get_agent_service),
) -> AgentResponse:
    try:
        agent = await service.get_agent(agent_id)

        return _to_response(agent)

    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{agent_id}/risk",
    response_model=AgentResponse,
)
async def update_agent_risk(
    agent_id: str,
    request: AgentUpdateRiskRequest,
    service: AgentService = Depends(get_agent_service),
) -> AgentResponse:
    try:
        agent = await service.update_risk(
            agent_id,
            risk_score=request.risk_score,
            risk_level=request.risk_level,
        )

        return _to_response(agent)

    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
