from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.domain.events.types import EventSeverity


@dataclass(slots=True)
class PolicyRule:
    """
    A single deterministic policy condition.
    """

    rule_id: str
    name: str
    description: str
    action: str
    priority: int = 100
    enabled: bool = True
    conditions: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PolicyDecision:
    """
    Result of evaluating an event or action against security policy.
    """

    decision: str
    policy_id: str
    policy_name: str
    reason: str
    severity: EventSeverity
    matched_rules: list[str] = field(default_factory=list)
    event_id: str | None = None
    tool: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def allowed(self) -> bool:
        return self.decision == "ALLOW"

    @property
    def blocked(self) -> bool:
        return self.decision == "DENY"


@dataclass(slots=True)
class PolicyEvaluationContext:
    """
    Provider-neutral context supplied to the policy engine.
    """

    event_id: str
    event_type: str
    tool: str | None = None
    sensitive_action: bool = False
    prompt_injection_detected: bool = False
    untrusted_content: bool = False
    external_transmission: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
