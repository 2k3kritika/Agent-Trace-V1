from __future__ import annotations

from datetime import datetime
from typing import Any

from app.schemas.common import APIModel


class DemoRunResponse(APIModel):
    scenario: str
    agent_id: str
    session_id: str

    risk_score: int
    risk_level: str

    attack_vector: str

    policy_decision: dict[str, Any]

    sensitive_action_attempted: bool
    sensitive_action_executed: bool
    action_blocked: bool
    external_transmission: bool

    events_persisted: int
    detections: int

    investigation_id: str | None

    forensics: dict[str, Any]

    generated_at: datetime
    note: str