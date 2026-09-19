from __future__ import annotations

from typing import Any

from app.adapters.base import AgentAdapter
from app.domain.events.models import CanonicalEvent
from app.domain.events.normalizer import EventNormalizer


class GenericLocalAdapter(AgentAdapter):
    """
    Generic adapter for local Python agents.

    A local agent only needs to emit a dictionary containing
    canonical-like telemetry fields. Provider-specific aliases
    are normalized here before entering AgentTrace.
    """

    adapter_name = "local"
    provider_name = "local"

    def __init__(
        self,
        *,
        normalizer: EventNormalizer | None = None,
    ) -> None:
        self.normalizer = normalizer or EventNormalizer()

    def normalize_event(
        self,
        raw_event: dict[str, Any],
        *,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> CanonicalEvent:
        normalized = self._prepare_event(
            raw_event,
            session_id=session_id,
            agent_id=agent_id,
        )

        return self.normalizer.normalize(
            normalized,
            default_session_id=session_id,
            default_agent_id=agent_id,
            default_provider=self.provider_name,
        )

    def _prepare_event(
        self,
        raw_event: dict[str, Any],
        *,
        session_id: str | None,
        agent_id: str | None,
    ) -> dict[str, Any]:
        event = dict(raw_event)

        event["event_id"] = event.get("event_id") or event.get("id")

        event["timestamp"] = (
            event.get("timestamp") or event.get("time") or event.get("created_at")
        )

        event["session_id"] = event.get("session_id") or session_id

        event["agent_id"] = event.get("agent_id") or event.get("agent") or agent_id

        event["provider"] = event.get("provider") or "local"

        event["source"] = event.get("source") or "local_adapter"

        event["event_type"] = (
            event.get("event_type") or event.get("type") or event.get("name")
        )

        event["status"] = event.get("status") or "RECEIVED"

        event["severity"] = event.get("severity") or "LOW"

        event["details"] = event.get("details") or {}

        event["metadata"] = event.get("metadata") or {}

        return event
