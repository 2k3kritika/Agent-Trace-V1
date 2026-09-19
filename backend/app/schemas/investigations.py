from datetime import datetime
from typing import Any

from app.core.constants import RiskLevel
from app.domain.events.types import EventSeverity
from app.schemas.common import APIModel
from pydantic import Field


class InvestigationCreateRequest(APIModel):
    session_id: str
    agent_id: str
    scenario: str | None = None
    status: str = "OPEN"
    risk_score: int = Field(default=0, ge=0, le=100)
    risk_level: RiskLevel = RiskLevel.LOW
    verdict_type: str | None = None
    attack_vector: str | None = None
    impact: str | None = None
    sensitive_action_attempted: bool = False
    sensitive_action_executed: bool = False
    policy_violation: bool = False
    action_blocked: bool = False
    external_transmission: bool = False
    summary: dict[str, Any] = Field(default_factory=dict)
    graph: dict[str, Any] = Field(default_factory=dict)


class InvestigationUpdateRequest(APIModel):
    status: str | None = None
    risk_score: int | None = Field(default=None, ge=0, le=100)
    risk_level: RiskLevel | None = None
    verdict_type: str | None = None
    attack_vector: str | None = None
    impact: str | None = None
    sensitive_action_attempted: bool | None = None
    sensitive_action_executed: bool | None = None
    policy_violation: bool | None = None
    action_blocked: bool | None = None
    external_transmission: bool | None = None
    summary: dict[str, Any] | None = None
    graph: dict[str, Any] | None = None


class InvestigationResponse(APIModel):
    id: str
    session_id: str
    agent_id: str

    status: str

    risk_score: int
    risk_level: RiskLevel

    scenario: str | None = None
    verdict_type: str | None = None
    attack_vector: str | None = None
    impact: str | None = None

    sensitive_action_attempted: bool
    sensitive_action_executed: bool
    policy_violation: bool
    action_blocked: bool
    external_transmission: bool

    summary: dict[str, Any] = Field(default_factory=dict)
    graph: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime
    updated_at: datetime


class InvestigationListResponse(APIModel):
    items: list[InvestigationResponse]
    page: int
    page_size: int
    total: int
    has_next: bool


class InvestigationEventSummary(APIModel):
    event_id: str
    event_type: str
    severity: EventSeverity
    timestamp: datetime


class InvestigationCloseRequest(APIModel):
    verdict_type: str | None = None
    impact: str | None = None
    summary: dict[str, Any] | None = None
