from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from app.domain.detection.models import DetectionFinding
from app.domain.events.models import CanonicalEvent
from app.domain.events.types import EventSeverity, EventStatus, EventType


def _combined_data(event: CanonicalEvent) -> dict[str, Any]:
    """
    Combine event details and metadata for rule evaluation.

    Details contain event-specific information while metadata contains
    adapter/provider context. Rules should be able to inspect both without
    depending on a particular provider.
    """
    data: dict[str, Any] = {}
    data.update(event.metadata)
    data.update(event.details)
    return data


def _is_true(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "yes",
            "1",
            "on",
            "enabled",
        }

    if isinstance(value, int):
        return value == 1

    return False


def _normalized_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip().lower()


class DetectionRule(ABC):
    """Base class for deterministic AgentTrace detection rules."""

    detector_id: str
    title: str
    severity: EventSeverity

    @abstractmethod
    def evaluate(self, event: CanonicalEvent) -> DetectionFinding | None:
        """Evaluate one canonical event and return a finding if detected."""


class UntrustedContentRule(DetectionRule):
    detector_id = "UNTRUSTED_CONTENT"
    title = "Untrusted Content Detected"
    severity = EventSeverity.MEDIUM

    _untrusted_levels: ClassVar[set[str]] = {
        "untrusted",
        "external",
        "unknown",
        "hostile",
        "malicious",
    }

    def evaluate(self, event: CanonicalEvent) -> DetectionFinding | None:
        data = _combined_data(event)

        trust_level = _normalized_text(
            data.get("trust_level") or data.get("trust") or data.get("content_trust")
        )

        explicitly_untrusted = any(
            _is_true(data.get(field))
            for field in (
                "untrusted",
                "is_untrusted",
                "external_content",
                "untrusted_content",
            )
        )

        detected_by_event_type = event.event_type == EventType.UNTRUSTED_CONTENT

        detected_by_trust_level = trust_level in self._untrusted_levels

        if not (
            detected_by_event_type or explicitly_untrusted or detected_by_trust_level
        ):
            return None

        source = event.source or data.get("source") or "unknown"

        return DetectionFinding(
            detector_id=self.detector_id,
            event_id=event.event_id,
            event_type=event.event_type,
            severity=self.severity,
            title=self.title,
            description=(
                "The agent processed content marked as untrusted or "
                "originating from an external/unknown source."
            ),
            confidence=1.0 if detected_by_event_type else 0.95,
            evidence={
                "source": source,
                "trust_level": trust_level or None,
                "event_type": event.event_type.value,
            },
            metadata={
                "rule": self.detector_id,
            },
        )


class PromptInjectionRule(DetectionRule):
    detector_id = "PROMPT_INJECTION_DETECTED"
    title = "Prompt Injection Detected"
    severity = EventSeverity.HIGH

    _indicator_phrases = (
        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore prior instructions",
        "disregard previous instructions",
        "disregard all previous instructions",
        "override the system prompt",
        "override system instructions",
        "reveal the system prompt",
        "reveal your system prompt",
        "show the system prompt",
        "developer message",
        "system message",
        "jailbreak",
        "do not follow the previous instructions",
        "new instructions",
    )

    def evaluate(self, event: CanonicalEvent) -> DetectionFinding | None:
        data = _combined_data(event)

        if event.event_type == EventType.PROMPT_INJECTION_DETECTED:
            matched_indicator = "explicit_event_type"
            confidence = 1.0
        else:
            text_fields = (
                data.get("content"),
                data.get("text"),
                data.get("body"),
                data.get("message"),
                data.get("prompt"),
                data.get("retrieved_content"),
            )

            searchable_text = " ".join(
                _normalized_text(value) for value in text_fields if value is not None
            )

            matched_indicator = next(
                (
                    phrase
                    for phrase in self._indicator_phrases
                    if phrase in searchable_text
                ),
                None,
            )

            if matched_indicator is None:
                return None

            confidence = 0.90

        return DetectionFinding(
            detector_id=self.detector_id,
            event_id=event.event_id,
            event_type=event.event_type,
            severity=self.severity,
            title=self.title,
            description=(
                "The event contains an explicit prompt-injection signal "
                "or instruction pattern attempting to influence the "
                "agent's instruction hierarchy."
            ),
            confidence=confidence,
            evidence={
                "matched_indicator": matched_indicator,
                "event_type": event.event_type.value,
            },
            metadata={
                "rule": self.detector_id,
            },
        )


class SensitiveActionRule(DetectionRule):
    detector_id = "SENSITIVE_ACTION_ATTEMPTED"
    title = "Sensitive Action Attempted"
    severity = EventSeverity.HIGH

    _sensitive_tools: ClassVar[set[str]] = {
        "send_email",
        "send_mail",
        "email",
        "http_post",
        "http_request",
        "upload_file",
        "upload",
        "delete_file",
        "delete",
        "execute_command",
        "shell",
        "run_command",
        "database_write",
        "db_write",
        "payment",
        "transfer_funds",
        "send_message",
        "publish",
    }

    _attempt_statuses: ClassVar[set[EventStatus]] = {
        EventStatus.REQUESTED,
        EventStatus.STARTED,
        EventStatus.ATTEMPTED,
        EventStatus.SIMULATED,
    }

    def evaluate(self, event: CanonicalEvent) -> DetectionFinding | None:
        data = _combined_data(event)

        explicitly_sensitive = any(
            _is_true(data.get(field))
            for field in (
                "sensitive",
                "is_sensitive",
                "sensitive_action",
                "sensitive_action_attempted",
            )
        )

        event_is_sensitive = event.event_type == EventType.SENSITIVE_ACTION_ATTEMPTED

        tool_name = _normalized_text(
            event.tool
            or data.get("tool")
            or data.get("tool_name")
            or data.get("action")
        )

        sensitive_tool = tool_name in self._sensitive_tools

        status_indicates_attempt = event.status in self._attempt_statuses

        if not (
            event_is_sensitive
            or explicitly_sensitive
            or (
                event.event_type == EventType.TOOL_CALL
                and sensitive_tool
                and status_indicates_attempt
            )
        ):
            return None

        executed = _is_true(
            data.get("executed")
            or data.get("action_executed")
            or data.get("sensitive_action_executed")
        )

        blocked = (
            _is_true(
                data.get("blocked")
                or data.get("action_blocked")
                or data.get("tool_blocked")
            )
            or event.status == EventStatus.BLOCKED
        )

        return DetectionFinding(
            detector_id=self.detector_id,
            event_id=event.event_id,
            event_type=event.event_type,
            severity=self.severity,
            title=self.title,
            description=(
                f"The agent attempted a sensitive action"
                f"{f' using tool {tool_name}' if tool_name else ''}."
            ),
            confidence=1.0 if event_is_sensitive else 0.90,
            evidence={
                "tool": tool_name or None,
                "executed": executed,
                "blocked": blocked,
                "event_status": event.status.value,
                "event_type": event.event_type.value,
            },
            metadata={
                "rule": self.detector_id,
            },
        )


class DetectionEngine:
    """
    Provider-neutral deterministic detection engine.

    The engine intentionally works only on CanonicalEvent objects. Adapters
    therefore remain responsible for translating provider-specific telemetry
    into the canonical AgentTrace event model.
    """

    def __init__(
        self,
        rules: list[DetectionRule] | None = None,
    ) -> None:
        self._rules = rules or [
            UntrustedContentRule(),
            PromptInjectionRule(),
            SensitiveActionRule(),
        ]

    @property
    def rules(self) -> tuple[DetectionRule, ...]:
        return tuple(self._rules)

    def detect(self, event: CanonicalEvent) -> list[DetectionFinding]:
        findings: list[DetectionFinding] = []

        for rule in self._rules:
            finding = rule.evaluate(event)

            if finding is not None:
                findings.append(finding)

        return findings

    def detect_many(
        self,
        events: list[CanonicalEvent],
    ) -> list[DetectionFinding]:
        findings: list[DetectionFinding] = []

        for event in events:
            findings.extend(self.detect(event))

        return findings
