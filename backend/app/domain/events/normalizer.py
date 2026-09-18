from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from app.domain.events.models import CanonicalEvent
from app.domain.events.types import (
    EventSeverity,
    EventStatus,
    EventType,
)


class EventNormalizationError(ValueError):
    """Raised when an incoming event cannot be normalized."""


class EventNormalizer:
    """
    Converts provider-specific telemetry into AgentTrace's
    canonical event representation.

    The normalizer deliberately does not perform database operations.
    """

    EVENT_TYPE_ALIASES: dict[str, EventType] = {
        "agent_start": EventType.AGENT_STARTED,
        "agent_started": EventType.AGENT_STARTED,
        "agent_complete": EventType.AGENT_COMPLETED,
        "agent_completed": EventType.AGENT_COMPLETED,
        "user_request": EventType.USER_REQUEST,
        "user.message": EventType.USER_REQUEST,
        "agent_response": EventType.AGENT_RESPONSE,
        "agent.message": EventType.AGENT_RESPONSE,
        "decision": EventType.AGENT_DECISION,
        "agent_decision": EventType.AGENT_DECISION,
        "tool_call": EventType.TOOL_CALL,
        "tool.call": EventType.TOOL_CALL,
        "tool_result": EventType.TOOL_RESULT,
        "tool.result": EventType.TOOL_RESULT,
        "content_retrieved": EventType.CONTENT_RETRIEVED,
        "retrieval": EventType.CONTENT_RETRIEVED,
        "untrusted_content": EventType.UNTRUSTED_CONTENT,
        "prompt_injection": EventType.PROMPT_INJECTION_DETECTED,
        "prompt_injection_detected": EventType.PROMPT_INJECTION_DETECTED,
        "sensitive_action": EventType.SENSITIVE_ACTION_ATTEMPTED,
        "sensitive_action_attempted": EventType.SENSITIVE_ACTION_ATTEMPTED,
        "policy_evaluation": EventType.POLICY_EVALUATION,
        "policy_violation": EventType.POLICY_VIOLATION,
        "tool_blocked": EventType.TOOL_BLOCKED,
        "tool_allowed": EventType.TOOL_ALLOWED,
        "error": EventType.ERROR,
    }

    STATUS_ALIASES: dict[str, EventStatus] = {
        "received": EventStatus.RECEIVED,
        "requested": EventStatus.REQUESTED,
        "started": EventStatus.STARTED,
        "succeeded": EventStatus.SUCCEEDED,
        "success": EventStatus.SUCCEEDED,
        "failed": EventStatus.FAILED,
        "attempted": EventStatus.ATTEMPTED,
        "blocked": EventStatus.BLOCKED,
        "allowed": EventStatus.ALLOWED,
        "simulated": EventStatus.SIMULATED,
        "completed": EventStatus.COMPLETED,
    }

    SEVERITY_ALIASES: dict[str, EventSeverity] = {
        "low": EventSeverity.LOW,
        "medium": EventSeverity.MEDIUM,
        "high": EventSeverity.HIGH,
        "critical": EventSeverity.CRITICAL,
    }

    def normalize(
        self,
        payload: Mapping[str, Any],
        *,
        provider: str | None = None,
        default_agent_id: str | None = None,
        default_session_id: str | None = None,
    ) -> CanonicalEvent:
        if not isinstance(payload, Mapping):
            raise EventNormalizationError(
                "Telemetry event must be a mapping/object."
            )

        event_id = self._required_string(
            payload,
            "event_id",
        )

        agent_id = self._optional_string(
            payload.get("agent_id")
        ) or default_agent_id

        session_id = self._optional_string(
            payload.get("session_id")
        ) or default_session_id

        if not agent_id:
            raise EventNormalizationError(
                "agent_id is required for canonical event normalization."
            )

        event_type = self._normalize_event_type(
            payload.get("event_type") or payload.get("type")
        )

        status = self._normalize_status(
            payload.get("status")
        )

        severity = self._normalize_severity(
            payload.get("severity")
        )

        timestamp = self._normalize_timestamp(
            payload.get("timestamp")
        )

        details = payload.get("details", {})

        if details is None:
            details = {}

        if not isinstance(details, Mapping):
            raise EventNormalizationError(
                "Event 'details' must be an object."
            )

        metadata = payload.get("metadata", {})

        if metadata is None:
            metadata = {}

        if not isinstance(metadata, Mapping):
            raise EventNormalizationError(
                "Event 'metadata' must be an object."
            )

        return CanonicalEvent(
            event_id=event_id,
            timestamp=timestamp,
            session_id=session_id,
            agent_id=agent_id,
            provider=(
                self._optional_string(payload.get("provider"))
                or provider
            ),
            event_type=event_type,
            status=status,
            tool=self._optional_string(payload.get("tool")),
            source=self._optional_string(payload.get("source")),
            severity=severity,
            details=dict(details),
            metadata=dict(metadata),
            parent_event_id=self._optional_string(
                payload.get("parent_event_id")
            ),
            related_event_id=self._optional_string(
                payload.get("related_event_id")
            ),
            trace_id=self._optional_string(
                payload.get("trace_id")
            ),
            span_id=self._optional_string(
                payload.get("span_id")
            ),
        )

    def normalize_many(
        self,
        payloads: list[Mapping[str, Any]],
        *,
        provider: str | None = None,
        default_agent_id: str | None = None,
        default_session_id: str | None = None,
    ) -> list[CanonicalEvent]:
        return [
            self.normalize(
                payload,
                provider=provider,
                default_agent_id=default_agent_id,
                default_session_id=default_session_id,
            )
            for payload in payloads
        ]

    def _normalize_event_type(
        self,
        value: Any,
    ) -> EventType:
        if isinstance(value, EventType):
            return value

        normalized = self._optional_string(value)

        if not normalized:
            raise EventNormalizationError(
                "event_type is required."
            )

        key = normalized.strip().lower()

        if key in self.EVENT_TYPE_ALIASES:
            return self.EVENT_TYPE_ALIASES[key]

        try:
            return EventType(key)
        except ValueError as exc:
            raise EventNormalizationError(
                f"Unsupported event_type: '{normalized}'."
            ) from exc

    def _normalize_status(
        self,
        value: Any,
    ) -> EventStatus:
        if value is None:
            return EventStatus.RECEIVED

        if isinstance(value, EventStatus):
            return value

        normalized = self._optional_string(value)

        if not normalized:
            return EventStatus.RECEIVED

        key = normalized.strip().lower()

        if key in self.STATUS_ALIASES:
            return self.STATUS_ALIASES[key]

        try:
            return EventStatus(key)
        except ValueError as exc:
            raise EventNormalizationError(
                f"Unsupported event status: '{normalized}'."
            ) from exc

    def _normalize_severity(
        self,
        value: Any,
    ) -> EventSeverity:
        if value is None:
            return EventSeverity.LOW

        if isinstance(value, EventSeverity):
            return value

        normalized = self._optional_string(value)

        if not normalized:
            return EventSeverity.LOW

        key = normalized.strip().lower()

        if key in self.SEVERITY_ALIASES:
            return self.SEVERITY_ALIASES[key]

        try:
            return EventSeverity(key)
        except ValueError as exc:
            raise EventNormalizationError(
                f"Unsupported event severity: '{normalized}'."
            ) from exc

    @staticmethod
    def _normalize_timestamp(
        value: Any,
    ) -> datetime:
        if value is None:
            return datetime.now(timezone.utc)

        if isinstance(value, datetime):
            timestamp = value
        elif isinstance(value, str):
            raw = value.strip()

            if raw.endswith("Z"):
                raw = raw[:-1] + "+00:00"

            try:
                timestamp = datetime.fromisoformat(raw)
            except ValueError as exc:
                raise EventNormalizationError(
                    f"Invalid timestamp: '{value}'."
                ) from exc
        else:
            raise EventNormalizationError(
                "timestamp must be an ISO-8601 string or datetime."
            )

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        return timestamp.astimezone(timezone.utc)

    @staticmethod
    def _required_string(
        payload: Mapping[str, Any],
        key: str,
    ) -> str:
        value = EventNormalizer._optional_string(
            payload.get(key)
        )

        if not value:
            raise EventNormalizationError(
                f"{key} is required."
            )

        return value

    @staticmethod
    def _optional_string(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        value = value.strip()

        return value or None