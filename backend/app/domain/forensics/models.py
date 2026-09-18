from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ForensicFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    finding_id: str
    investigation_id: str
    finding_type: str
    severity: str
    title: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    event_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    indicators: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AttackGraphNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    node_type: str
    label: str
    event_id: str | None = None
    severity: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttackGraphEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    edge_id: str
    source: str
    target: str
    relationship: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttackGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodes: list[AttackGraphNode] = Field(default_factory=list)
    edges: list[AttackGraphEdge] = Field(default_factory=list)


class ForensicAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    investigation_id: str
    findings: list[ForensicFinding] = Field(default_factory=list)
    graph: AttackGraph
    evidence_count: int = 0
    security_event_count: int = 0
    timeline_start: datetime | None = None
    timeline_end: datetime | None = None
    summary: dict[str, Any] = Field(default_factory=dict)