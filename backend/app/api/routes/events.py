from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.exceptions import NotFoundError
from app.schemas.events import (
    CanonicalEventResponse,
    EventListResponse,
)
from app.services.dependency import (
    get_event_service,
)
from app.services.event_service import EventService

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


def _to_response(event) -> CanonicalEventResponse:
    return CanonicalEventResponse.model_validate(
        event,
        from_attributes=True,
    )


@router.get(
    "",
    response_model=EventListResponse,
)
async def list_events(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=25,
        ge=1,
        le=100,
    ),
    session_id: str | None = None,
    agent_id: str | None = None,
    event_type: str | None = None,
    severity: str | None = None,
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    search: str | None = None,
    service: EventService = Depends(get_event_service),
) -> EventListResponse:
    result = await service.list_events(
        page=page,
        page_size=page_size,
        session_id=session_id,
        agent_id=agent_id,
        event_type=event_type,
        severity=severity,
        status=status_filter,
        search=search,
    )

    return EventListResponse(
        items=[_to_response(event) for event in result.items],
        page=page,
        page_size=page_size,
        total=result.total,
        has_next=(page * page_size < result.total),
    )


@router.get(
    "/security",
    response_model=EventListResponse,
)
async def list_security_events(
    session_id: str | None = None,
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    service: EventService = Depends(get_event_service),
) -> EventListResponse:
    result = await service.list_security_events(
        session_id=session_id,
        page=page,
        page_size=page_size,
    )

    return EventListResponse(
        items=[_to_response(event) for event in result.items],
        page=page,
        page_size=page_size,
        total=result.total,
        has_next=(page * page_size < result.total),
    )


@router.get(
    "/session/{session_id}",
    response_model=EventListResponse,
)
async def list_session_events(
    session_id: str,
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    service: EventService = Depends(get_event_service),
) -> EventListResponse:
    result = await service.list_session_events(
        session_id,
        page=page,
        page_size=page_size,
    )

    return EventListResponse(
        items=[_to_response(event) for event in result.items],
        page=page,
        page_size=page_size,
        total=result.total,
        has_next=(page * page_size < result.total),
    )


@router.get(
    "/{event_id}",
    response_model=CanonicalEventResponse,
)
async def get_event(
    event_id: str,
    service: EventService = Depends(get_event_service),
) -> CanonicalEventResponse:
    try:
        event = await service.get_event(event_id)

        return _to_response(event)

    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
