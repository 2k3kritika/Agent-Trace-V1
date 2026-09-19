from __future__ import annotations

from typing import Any

from app.domain.events.types import EventSeverity
from app.schemas.common import APIModel
from pydantic import Field


class RiskContributionResponse(APIModel):
    source_id: str
    source_type: str
    description: str
    points: int
    severity: EventSeverity
    event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RiskAssessmentResponse(APIModel):
    score: int = Field(ge=0, le=100)
    level: str
    contributions: list[RiskContributionResponse] = Field(default_factory=list)
    factors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RiskEventRequest(APIModel):
    """
    Input for calculating risk from one event's security characteristics.
    """

    event_id: str
    event_type: str
    severity: EventSeverity
    detector_id: str | None = None
    sensitive_action: bool = False
    prompt_injection_detected: bool = False
    untrusted_content: bool = False
    policy_violation: bool = False
    action_blocked: bool = False
    external_transmission: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class RiskBatchRequest(APIModel):
    events: list[RiskEventRequest] = Field(
        min_length=1,
        max_length=1000,
    )


class RiskBatchResponse(APIModel):
    assessment: RiskAssessmentResponse
