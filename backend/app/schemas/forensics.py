from datetime import datetime
from typing import Any

from app.schemas.common import APIModel
from pydantic import Field


class ForensicAnalysisRequest(APIModel):
    include_timeline: bool = True
    include_attack_graph: bool = True
    include_findings: bool = True


class ForensicFindingResponse(APIModel):
    rule_id: str
    title: str
    description: str
    severity: str
    confidence: float = Field(ge=0.0, le=1.0)
    event_ids: list[str] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ForensicTimelineItem(APIModel):
    event_id: str
    timestamp: datetime
    event_type: str
    severity: str
    status: str
    tool: str | None = None
    title: str | None = None


class AttackGraphNodeResponse(APIModel):
    node_id: str
    node_type: str
    label: str
    event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttackGraphEdgeResponse(APIModel):
    source: str
    target: str
    relationship_type: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttackGraphResponse(APIModel):
    nodes: list[AttackGraphNodeResponse] = Field(default_factory=list)
    edges: list[AttackGraphEdgeResponse] = Field(default_factory=list)


class ForensicAnalysisResponse(APIModel):
    investigation_id: str
    event_count: int
    security_event_count: int
    suspicious_event_count: int
    sensitive_action_count: int
    blocked_action_count: int

    findings: list[ForensicFindingResponse] = Field(default_factory=list)

    timeline: list[ForensicTimelineItem] = Field(default_factory=list)

    graph: AttackGraphResponse | None = None

    summary: str
