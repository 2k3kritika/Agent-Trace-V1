from fastapi import APIRouter, Depends

from app.domain.events.models import CanonicalEvent
from app.schemas.correlation import (
    CorrelationRequest,
    CorrelationResponse,
)
from app.services.correlation_service import CorrelationService
from app.services.dependency import (
    get_correlation_service,
    get_event_service,
)
from app.services.event_service import EventService


router = APIRouter(
    prefix="/correlation",
    tags=["Correlation"],
)


@router.post(
    "/sessions/{session_id}",
    response_model=CorrelationResponse,
)
async def correlate_session(
    session_id: str,
    request: CorrelationRequest | None = None,
    event_service: EventService = Depends(get_event_service),
    correlation_service: CorrelationService = Depends(get_correlation_service),
) -> CorrelationResponse:
    event_responses = await event_service.list_session_events(session_id)

    events = [
        CanonicalEvent.model_validate(
            event.model_dump(mode="python")
        )
        for event in event_responses
    ]

    return correlation_service.correlate(
        session_id=session_id,
        events=events,
        request=request,
    )