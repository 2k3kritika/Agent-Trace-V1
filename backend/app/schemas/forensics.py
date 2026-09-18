from datetime import datetime
from typing import Any

from app.schemas.common import APIModel
from app.domain.forensics.models import (
    AttackGraph,
    ForensicFinding,
)


class ForensicAnalysisRequest(APIModel):
    investigation_id: str


class ForensicFindingResponse(APIModel):
    finding_id: str
    investigation_id: str
    finding_type: str
    severity: str
    title: str
    description: str
    confidence: float
    event_ids: list[str]
    evidence_ids: list[str]
    indicators: list[str]
    metadata: dict[str, Any]
    created_at: datetime


class ForensicAnalysisResponse(APIModel):
    investigation_id: str
    findings: list[ForensicFindingResponse]
    graph: AttackGraph
    evidence_count: int
    security_event_count: int
    timeline_start: datetime | None
    timeline_end: datetime | None
    summary: dict[str, Any]


def finding_to_response(
    finding: ForensicFinding,
) -> ForensicFindingResponse:
    return ForensicFindingResponse(
        finding_id=finding.finding_id,
        investigation_id=finding.investigation_id,
        finding_type=finding.finding_type,
        severity=finding.severity,
        title=finding.title,
        description=finding.description,
        confidence=finding.confidence,
        event_ids=finding.event_ids,
        evidence_ids=finding.evidence_ids,
        indicators=finding.indicators,
        metadata=finding.metadata,
        created_at=finding.created_at,
    )