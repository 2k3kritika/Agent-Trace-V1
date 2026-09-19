from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any, ClassVar

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
    Converts provider-specific/raw event payloads into CanonicalEvent objects.

    The normalizer intentionally provides safe defaults for optional
    session/provider information so that provider adapters can progressively
    enrich events without making normalization unnecessarily brittle.
    """

    EVENT_TYPE_ALIASES: ClassVar[dict[str, EventType]] = {
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

    def normalize(
        self,
        payload: dict[str, Any],
        *,
        provider: str | None = None,
        default_agent_id: str | None = None,
        default_session_id: str | None = None,
    ) -> CanonicalEvent:
        if not isinstance(payload, dict):
            raise EventNormalizationError("Event payload must be a dictionary")

        event_id = self._required_string(payload.get("event_id"), "event_id")

        agent_id = self._optional_string(
            payload.get("agent_id")
        ) or self._optional_string(default_agent_id)

        if not agent_id:
            raise EventNormalizationError(
                "agent_id is required or must be supplied through default_agent_id"
            )

        # Session IDs are useful but should not make normalization fail when
        # processing provider events that do not expose session information.
        session_id = (
            self._optional_string(payload.get("session_id"))
            or self._optional_string(default_session_id)
            or "unknown-session"
        )

        # Provider is similarly allowed to fall back to a neutral value.
        provider_name = (
            self._optional_string(payload.get("provider"))
            or self._optional_string(provider)
            or "unknown"
        )

        event_type = self._normalize_event_type(payload.get("event_type"))

        status = self._normalize_enum(
            payload.get("status"),
            EventStatus,
            default=EventStatus.RECEIVED,
            field_name="status",
        )

        severity = self._normalize_enum(
            payload.get("severity"),
            EventSeverity,
            default=EventSeverity.LOW,
            field_name="severity",
        )

        timestamp = self._normalize_timestamp(payload.get("timestamp"))

        details = payload.get("details") or {}
        metadata = payload.get("metadata") or {}

        if not isinstance(details, dict):
            raise EventNormalizationError("details must be a dictionary")

        if not isinstance(metadata, dict):
            raise EventNormalizationError("metadata must be a dictionary")

        return CanonicalEvent(
            event_id=event_id,
            timestamp=timestamp,
            session_id=session_id,
            agent_id=agent_id,
            provider=provider_name,
            event_type=event_type,
            status=status,
            tool=self._optional_string(payload.get("tool")),
            source=self._optional_string(payload.get("source")),
            severity=severity,
            details=details,
            metadata=metadata,
            parent_event_id=self._optional_string(payload.get("parent_event_id")),
            related_event_id=self._optional_string(payload.get("related_event_id")),
            trace_id=self._optional_string(payload.get("trace_id")),
            span_id=self._optional_string(payload.get("span_id")),
        )

    def normalize_many(
        self,
        payloads: Iterable[dict[str, Any]],
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

    def _normalize_event_type(self, value: Any) -> EventType:
        if isinstance(value, EventType):
            return value

        raw = self._required_string(value, "event_type")
        normalized = raw.strip().lower()

        alias = self.EVENT_TYPE_ALIASES.get(normalized)
        if alias is not None:
            return alias

        try:
            return EventType(raw.strip().upper())
        except ValueError as exc:
            raise EventNormalizationError(f"Unsupported event_type: {value!r}") from exc

    @staticmethod
    def _normalize_enum(
        value: Any,
        enum_type: type,
        *,
        default: Any,
        field_name: str,
    ) -> Any:
        if value is None or value == "":
            return default

        if isinstance(value, enum_type):
            return value

        try:
            return enum_type(str(value).strip().upper())
        except ValueError as exc:
            raise EventNormalizationError(
                f"Unsupported {field_name}: {value!r}"
            ) from exc

    @staticmethod
    def _normalize_timestamp(value: Any) -> datetime:
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
                raise EventNormalizationError(f"Invalid timestamp: {value!r}") from exc
        else:
            raise EventNormalizationError(
                "timestamp must be a datetime or ISO-8601 string"
            )

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        return timestamp

    @staticmethod
    def _required_string(value: Any, field_name: str) -> str:
        result = EventNormalizer._optional_string(value)

        if not result:
            raise EventNormalizationError(f"{field_name} is required")

        return result

    @staticmethod
    def _optional_string(value: Any) -> str | None:
        if value is None:
            return None

        result = str(value).strip()

        return result if result else None
