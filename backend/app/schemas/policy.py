from __future__ import annotations

from typing import Any

from pydantic import Field

from app.domain.events.types import EventSeverity
from app.schemas.common import APIModel


class PolicyEvaluationRequest(APIModel):
    event_id: str
    event_type: str
    tool: str | None = None

    sensitive_action: bool = False
    prompt_injection_detected: bool = False
    untrusted_content: bool = False
    external_transmission: bool = False

    metadata: dict[str, Any] = Field(default_factory=dict)


class PolicyDecisionResponse(APIModel):
    decision: str
    policy_id: str
    policy_name: str
    reason: str
    severity: EventSeverity
    matched_rules: list[str] = Field(default_factory=list)

    event_id: str | None = None
    tool: str | None = None

    allowed: bool
    blocked: bool

    metadata: dict[str, Any] = Field(default_factory=dict)