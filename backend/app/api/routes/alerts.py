from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.domain.events.types import EventSeverity
from app.schemas.alerts import (
    AlertCreateRequest,
    AlertListResponse,
    AlertResponse,
)
from app.services.alert_service import AlertService
from app.services.dependency import get_alert_service


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


def _alert_to_response(alert) -> AlertResponse:
    return AlertResponse(
        alert_id=alert.alert_id,
        title=alert.title,
        description=alert.description,
        severity=alert.severity,
        status=alert.status,
        agent_id=alert.agent_id,
        session_id=alert.session_id,
        investigation_id=alert.investigation_id,
        detector_id=alert.detector_id,
        created_at=alert.created_at.isoformat(),
        updated_at=alert.updated_at.isoformat(),
        metadata=alert.metadata or {},
    )


@router.post(
    "",
    response_model=AlertResponse,
)
async def create_alert(
    request: AlertCreateRequest,
    service: AlertService = Depends(get_alert_service),
) -> AlertResponse:
    alert = await service.create_alert(
        title=request.title,
        description=request.description,
        severity=request.severity,
        agent_id=request.agent_id,
        session_id=request.session_id,
        investigation_id=request.investigation_id,
        detector_id=request.detector_id,
        metadata=request.metadata,
    )

    return _alert_to_response(alert)


@router.get(
    "",
    response_model=AlertListResponse,
)
async def list_alerts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    severity: EventSeverity | None = None,
    status: str | None = None,
    service: AlertService = Depends(get_alert_service),
) -> AlertListResponse:
    result = await service.list_alerts(
        page=page,
        page_size=page_size,
        severity=severity,
        status=status,
    )

    items = [
        _alert_to_response(alert)
        for alert in result.items
    ]

    return AlertListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=result.total,
        has_next=(page * page_size) < result.total,
    )


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
)
async def get_alert(
    alert_id: str,
    service: AlertService = Depends(get_alert_service),
) -> AlertResponse:
    alert = await service.get_alert(alert_id)

    return _alert_to_response(alert)