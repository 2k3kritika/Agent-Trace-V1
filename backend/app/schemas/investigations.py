from __future__ import annotations

from typing import Any

from pydantic import Field

from app.domain.events.types import EventSeverity
from app.schemas.common import APIModel


class InvestigationCreateRequest(APIModel):
    session_id: str | None = None
    agent_id: str | None = None

    scenario: str | None = None

    risk_score: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    risk_level: str = "LOW"

    verdict_type: str | None = None
    attack_vector: str | None = None
    impact: str | None = None

    sensitive_action_attempted: bool = False
    sensitive_action_executed: bool = False
    policy_violation: bool = False
    action_blocked: bool = False
    external_transmission: bool = False

    summary: dict[str, Any] = Field(
        default_factory=dict
    )

    graph: dict[str, Any] = Field(
        default_factory=dict
    )


class InvestigationUpdateRequest(APIModel):
    status: str | None = None

    risk_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    risk_level: str | None = None

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
    investigation_id: str

    session_id: str | None = None
    agent_id: str | None = None

    status: str

    risk_score: int
    risk_level: str

    scenario: str | None = None

    verdict_type: str | None = None
    attack_vector: str | None = None
    impact: str | None = None

    sensitive_action_attempted: bool
    sensitive_action_executed: bool
    policy_violation: bool
    action_blocked: bool
    external_transmission: bool

    summary: dict[str, Any] = Field(
        default_factory=dict
    )

    graph: dict[str, Any] = Field(
        default_factory=dict
    )

    created_at: str
    updated_at: str


class InvestigationListResponse(APIModel):
    items: list[InvestigationResponse] = Field(
        default_factory=list
    )
    page: int
    page_size: int
    total: int
    has_next: bool