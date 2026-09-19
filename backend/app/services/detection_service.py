from __future__ import annotations

from app.domain.detection.models import (
    DetectionBatchResult,
    DetectionFinding,
    DetectionResult,
)
from app.domain.detection.rules import DetectionEngine
from app.domain.events.models import CanonicalEvent


class DetectionService:
    """
    Application service responsible for running security detection.

    Detection is deliberately separated from persistence.

    The service:
        CanonicalEvent
            ↓
        DetectionEngine
            ↓
        DetectionFinding

    Later services can consume findings for alerts, risk scoring,
    investigations, evidence, and forensic analysis.
    """

    def __init__(
        self,
        engine: DetectionEngine | None = None,
    ) -> None:
        self.engine = engine or DetectionEngine()

    def detect_event(
        self,
        event: CanonicalEvent,
    ) -> DetectionResult:
        findings = self.engine.detect(event)

        return DetectionResult(
            event_id=event.event_id,
            findings=findings,
        )

    def detect_events(
        self,
        events: list[CanonicalEvent],
    ) -> DetectionBatchResult:
        results = [self.detect_event(event) for event in events]

        return DetectionBatchResult(results=results)

    def detect_event_findings(
        self,
        event: CanonicalEvent,
    ) -> list[DetectionFinding]:
        return self.engine.detect(event)

    def detect_many_findings(
        self,
        events: list[CanonicalEvent],
    ) -> list[DetectionFinding]:
        return self.engine.detect_many(events)
