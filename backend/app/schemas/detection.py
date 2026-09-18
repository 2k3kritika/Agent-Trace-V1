from __future__ import annotations

from typing import Any

from pydantic import Field

from app.domain.events.types import EventSeverity
from app.schemas.common import APIModel
from app.schemas.events import CanonicalEventCreate


class DetectionFindingResponse(APIModel):
    detector_id: str
    event_id: str
    event_type: str
    severity: EventSeverity
    title: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DetectionResultResponse(APIModel):
    event_id: str
    detected: bool
    findings: list[DetectionFindingResponse] = Field(
        default_factory=list
    )
    highest_severity: EventSeverity | None = None


class DetectionBatchResponse(APIModel):
    results: list[DetectionResultResponse] = Field(
        default_factory=list
    )
    findings: list[DetectionFindingResponse] = Field(
        default_factory=list
    )
    detected_count: int = 0


class DetectionRequest(APIModel):
    """
    Request for running detection against a single canonical event.
    """

    event: CanonicalEventCreate


class DetectionBatchRequest(APIModel):
    """
    Request for running detection against multiple canonical events.
    """

    events: list[CanonicalEventCreate] = Field(
        min_length=1,
        max_length=1000,
    )