from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.domain.events.types import EventSeverity, EventType


@dataclass(slots=True)
class DetectionFinding:
    """
    A normalized security finding produced by a detection rule.

    Findings are intentionally independent of persistence. The detection
    engine produces findings, and later services decide whether a finding
    becomes an alert, investigation evidence, risk contribution, etc.
    """

    detector_id: str
    event_id: str
    event_type: EventType
    severity: EventSeverity
    title: str
    description: str
    confidence: float = 1.0
    evidence: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass(slots=True)
class DetectionResult:
    """Result of running all configured detection rules."""

    event_id: str
    findings: list[DetectionFinding] = field(default_factory=list)

    @property
    def detected(self) -> bool:
        return bool(self.findings)

    @property
    def highest_severity(self) -> EventSeverity | None:
        if not self.findings:
            return None

        severity_order = {
            EventSeverity.LOW: 1,
            EventSeverity.MEDIUM: 2,
            EventSeverity.HIGH: 3,
            EventSeverity.CRITICAL: 4,
        }

        return max(
            self.findings,
            key=lambda finding: severity_order[finding.severity],
        ).severity


@dataclass(slots=True)
class DetectionBatchResult:
    """Result of running detection across multiple events."""

    results: list[DetectionResult] = field(default_factory=list)

    @property
    def findings(self) -> list[DetectionFinding]:
        return [finding for result in self.results for finding in result.findings]

    @property
    def detected_count(self) -> int:
        return sum(1 for result in self.results if result.detected)
