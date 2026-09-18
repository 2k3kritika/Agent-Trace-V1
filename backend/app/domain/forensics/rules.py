from uuid import uuid4

from app.domain.events.models import CanonicalEvent
from app.domain.events.types import (
    EventSeverity,
    EventType,
)
from app.domain.forensics.models import ForensicFinding


class ForensicRule:
    rule_id: str = "base"

    def evaluate(
        self,
        investigation_id: str,
        events: list[CanonicalEvent],
    ) -> list[ForensicFinding]:
        raise NotImplementedError


class PromptInjectionChainRule(ForensicRule):
    rule_id = "prompt-injection-chain"

    def evaluate(
        self,
        investigation_id: str,
        events: list[CanonicalEvent],
    ) -> list[ForensicFinding]:
        injection_events = [
            event
            for event in events
            if event.event_type == EventType.PROMPT_INJECTION_DETECTED
        ]

        if not injection_events:
            return []

        event_ids = [event.event_id for event in injection_events]

        return [
            ForensicFinding(
                finding_id=str(uuid4()),
                investigation_id=investigation_id,
                finding_type="PROMPT_INJECTION_CHAIN",
                severity=EventSeverity.HIGH.value,
                title="Prompt injection activity detected",
                description=(
                    "One or more telemetry events indicate that "
                    "untrusted content attempted to influence agent behavior."
                ),
                confidence=0.95,
                event_ids=event_ids,
                indicators=[
                    "PROMPT_INJECTION_DETECTED",
                ],
            )
        ]


class SensitiveActionAfterInjectionRule(ForensicRule):
    rule_id = "sensitive-action-after-injection"

    def evaluate(
        self,
        investigation_id: str,
        events: list[CanonicalEvent],
    ) -> list[ForensicFinding]:
        injection_indexes = [
            index
            for index, event in enumerate(events)
            if event.event_type
            == EventType.PROMPT_INJECTION_DETECTED
        ]

        action_indexes = [
            index
            for index, event in enumerate(events)
            if event.event_type
            == EventType.SENSITIVE_ACTION_ATTEMPTED
        ]

        if not injection_indexes or not action_indexes:
            return []

        related_events: list[CanonicalEvent] = []

        for action_index in action_indexes:
            previous_injection = any(
                injection_index <= action_index
                for injection_index in injection_indexes
            )

            if previous_injection:
                related_events.append(events[action_index])

        if not related_events:
            return []

        event_ids = [
            event.event_id
            for event in related_events
        ]

        return [
            ForensicFinding(
                finding_id=str(uuid4()),
                investigation_id=investigation_id,
                finding_type="INJECTION_TO_SENSITIVE_ACTION",
                severity=EventSeverity.CRITICAL.value,
                title="Sensitive action followed prompt injection",
                description=(
                    "A sensitive action attempt occurred after "
                    "prompt-injection activity in the same investigation."
                ),
                confidence=0.98,
                event_ids=event_ids,
                indicators=[
                    "PROMPT_INJECTION_DETECTED",
                    "SENSITIVE_ACTION_ATTEMPTED",
                ],
            )
        ]


class PolicyViolationRule(ForensicRule):
    rule_id = "policy-violation"

    def evaluate(
        self,
        investigation_id: str,
        events: list[CanonicalEvent],
    ) -> list[ForensicFinding]:
        violations = [
            event
            for event in events
            if event.event_type == EventType.POLICY_VIOLATION
        ]

        if not violations:
            return []

        return [
            ForensicFinding(
                finding_id=str(uuid4()),
                investigation_id=investigation_id,
                finding_type="POLICY_VIOLATION",
                severity=EventSeverity.HIGH.value,
                title="Policy violation recorded",
                description=(
                    "The agent attempted an action that violated "
                    "an active security policy."
                ),
                confidence=0.99,
                event_ids=[
                    event.event_id
                    for event in violations
                ],
                indicators=[
                    "POLICY_VIOLATION",
                ],
            )
        ]


class ToolBlockedRule(ForensicRule):
    rule_id = "tool-blocked"

    def evaluate(
        self,
        investigation_id: str,
        events: list[CanonicalEvent],
    ) -> list[ForensicFinding]:
        blocked = [
            event
            for event in events
            if event.event_type == EventType.TOOL_BLOCKED
        ]

        if not blocked:
            return []

        return [
            ForensicFinding(
                finding_id=str(uuid4()),
                investigation_id=investigation_id,
                finding_type="TOOL_BLOCKED",
                severity=EventSeverity.MEDIUM.value,
                title="Security policy blocked a tool action",
                description=(
                    "A potentially sensitive tool action was prevented "
                    "by the security policy."
                ),
                confidence=0.99,
                event_ids=[
                    event.event_id
                    for event in blocked
                ],
                indicators=[
                    "TOOL_BLOCKED",
                ],
            )
        ]


DEFAULT_FORENSIC_RULES: tuple[ForensicRule, ...] = (
    PromptInjectionChainRule(),
    SensitiveActionAfterInjectionRule(),
    PolicyViolationRule(),
    ToolBlockedRule(),
)