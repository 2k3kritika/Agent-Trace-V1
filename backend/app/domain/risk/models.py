from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.domain.events.types import EventSeverity


@dataclass(slots=True)
class RiskContribution:
    """
    Individual contribution to an overall risk score.

    Each detection finding can contribute independently. Keeping these
    contributions explicit makes the final risk score explainable to the
    frontend and useful during investigations.
    """

    source_id: str
    source_type: str
    description: str
    points: int
    severity: EventSeverity
    event_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RiskAssessment:
    """
    Aggregate risk assessment for an agent/session/investigation context.
    """

    score: int
    level: str
    contributions: list[RiskContribution] = field(default_factory=list)
    factors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.score = max(0, min(100, int(self.score)))

        if self.level not in {
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        }:
            raise ValueError(
                "Risk level must be LOW, MEDIUM, HIGH, or CRITICAL"
            )


@dataclass(slots=True)
class RiskContext:
    """
    Optional contextual information used by the risk engine.

    These fields allow later investigation/session-level scoring without
    changing the basic detection model.
    """

    event_count: int = 0
    security_event_count: int = 0
    sensitive_action_attempted: bool = False
    sensitive_action_executed: bool = False
    policy_violation: bool = False
    action_blocked: bool = False
    external_transmission: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)