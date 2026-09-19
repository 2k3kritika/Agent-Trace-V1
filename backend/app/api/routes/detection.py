from __future__ import annotations

from fastapi import APIRouter, Depends

from app.domain.events.models import CanonicalEvent
from app.schemas.detection import (
    DetectionBatchRequest,
    DetectionBatchResponse,
    DetectionFindingResponse,
    DetectionRequest,
    DetectionResultResponse,
)
from app.services.dependency import get_detection_service
from app.services.detection_service import DetectionService

router = APIRouter(
    prefix="/detection",
    tags=["Detection"],
)


def _finding_to_response(
    finding,
) -> DetectionFindingResponse:
    return DetectionFindingResponse(
        detector_id=finding.detector_id,
        event_id=finding.event_id,
        event_type=finding.event_type.value,
        severity=finding.severity,
        title=finding.title,
        description=finding.description,
        confidence=finding.confidence,
        evidence=finding.evidence,
        metadata=finding.metadata,
    )


def _result_to_response(
    result,
) -> DetectionResultResponse:
    return DetectionResultResponse(
        event_id=result.event_id,
        detected=result.detected,
        findings=[_finding_to_response(finding) for finding in result.findings],
        highest_severity=result.highest_severity,
    )


@router.post(
    "/event",
    response_model=DetectionResultResponse,
)
async def detect_event(
    request: DetectionRequest,
    service: DetectionService = Depends(get_detection_service),
) -> DetectionResultResponse:
    """
    Run all configured security detectors against one event.
    """

    event = CanonicalEvent.model_validate(request.event.model_dump())

    result = service.detect_event(event)

    return _result_to_response(result)


@router.post(
    "/events",
    response_model=DetectionBatchResponse,
)
async def detect_events(
    request: DetectionBatchRequest,
    service: DetectionService = Depends(get_detection_service),
) -> DetectionBatchResponse:
    """
    Run all configured security detectors against a batch of events.
    """

    events = [
        CanonicalEvent.model_validate(event.model_dump()) for event in request.events
    ]

    batch_result = service.detect_events(events)

    return DetectionBatchResponse(
        results=[_result_to_response(result) for result in batch_result.results],
        findings=[_finding_to_response(finding) for finding in batch_result.findings],
        detected_count=batch_result.detected_count,
    )
