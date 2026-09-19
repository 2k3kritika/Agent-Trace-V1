from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import AgentTraceError
from app.schemas.telemetry import (
    TelemetryBatchRequest,
    TelemetryBatchResponse,
    TelemetryEventRequest,
    TelemetryIngestResponse,
)
from app.services.dependency import get_telemetry_service
from app.services.telemetry_service import TelemetryService

router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"],
)


@router.post(
    "/events",
    response_model=TelemetryIngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def ingest_event(
    request: TelemetryEventRequest,
    service: TelemetryService = Depends(get_telemetry_service),
) -> TelemetryIngestResponse:
    try:
        return await service.ingest_event(request)

    except AgentTraceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc


@router.post(
    "/events/batch",
    response_model=TelemetryBatchResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def ingest_event_batch(
    request: TelemetryBatchRequest,
    service: TelemetryService = Depends(get_telemetry_service),
) -> TelemetryBatchResponse:
    try:
        return await service.ingest_batch(request)

    except AgentTraceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc
