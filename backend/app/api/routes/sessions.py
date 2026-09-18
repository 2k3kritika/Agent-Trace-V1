from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.exceptions import NotFoundError
from app.schemas.sessions import (
    SessionCreateRequest,
    SessionListResponse,
    SessionResponse,
)
from app.services.dependency import get_session_service
from app.services.session_service import SessionService


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


def _to_response(session) -> SessionResponse:
    return SessionResponse.model_validate(
        session,
        from_attributes=True,
    )


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    request: SessionCreateRequest,
    service: SessionService = Depends(
        get_session_service
    ),
) -> SessionResponse:
    session, _ = await service.create_session(
        session_id=request.session_id,
        agent_id=request.agent_id,
        provider=request.provider,
        scenario=request.scenario,
        metadata=request.metadata,
    )

    return _to_response(session)


@router.get(
    "",
    response_model=SessionListResponse,
)
async def list_sessions(
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
    risk_level: str | None = None,
    search: str | None = None,
    service: SessionService = Depends(
        get_session_service
    ),
) -> SessionListResponse:
    result = await service.list_sessions(
        page=page,
        page_size=page_size,
        agent_id=agent_id,
        status=status_filter,
        risk_level=risk_level,
        search=search,
    )

    return SessionListResponse(
        items=[
            _to_response(session)
            for session in result.items
        ],
        page=page,
        page_size=page_size,
        total=result.total,
        has_next=(
            page * page_size < result.total
        ),
    )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
)
async def get_session(
    session_id: str,
    service: SessionService = Depends(
        get_session_service
    ),
) -> SessionResponse:
    try:
        session = await service.get_session(
            session_id
        )

        return _to_response(session)

    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{session_id}/close",
    response_model=SessionResponse,
)
async def close_session(
    session_id: str,
    service: SessionService = Depends(
        get_session_service
    ),
) -> SessionResponse:
    try:
        session = await service.close_session(
            session_id
        )

        return _to_response(session)

    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc