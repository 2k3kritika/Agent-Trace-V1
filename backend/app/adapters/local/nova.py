from __future__ import annotations

from typing import Any, ClassVar

from app.adapters.local.generic import GenericLocalAdapter
from app.domain.events.models import CanonicalEvent


class NovaAdapter(GenericLocalAdapter):
    """
    Adapter for the existing Nova customer-service agent.

    Nova remains responsible for its own application/UI.
    AgentTrace is responsible for normalization and security
    interpretation.
    """

    adapter_name = "nova"
    provider_name = "local"

    _EVENT_ALIASES: ClassVar[dict[str, str]] = {
        "agent_started": "AGENT_STARTED",
        "started": "AGENT_STARTED",

        "user_request": "USER_REQUEST",
        "user_message": "USER_REQUEST",

        "tool_call": "TOOL_CALL",
        "tool_invocation": "TOOL_CALL",

        "tool_result": "TOOL_RESULT",
        "tool_response": "TOOL_RESULT",

        "content_retrieved": "CONTENT_RETRIEVED",
        "retrieved_content": "CONTENT_RETRIEVED",

        "agent_decision": "AGENT_DECISION",
        "decision": "AGENT_DECISION",

        "sensitive_action_attempted": (
            "SENSITIVE_ACTION_ATTEMPTED"
        ),

        "agent_completed": "AGENT_COMPLETED",
        "completed": "AGENT_COMPLETED",
    }

    def normalize_event(
        self,
        raw_event: dict[str, Any],
        *,
        session_id: str | None = None,
        agent_id: str | None = "nova",
    ) -> CanonicalEvent:
        event = dict(raw_event)

        raw_type = str(
            event.get("event_type")
            or event.get("type")
            or event.get("name")
            or ""
        ).strip()

        canonical_type = self._EVENT_ALIASES.get(
            raw_type.lower(),
            raw_type.upper(),
        )

        event["event_type"] = canonical_type

        event["agent_id"] = (
            event.get("agent_id")
            or agent_id
            or "nova"
        )

        event["provider"] = "local"

        event["source"] = (
            event.get("source")
            or "nova_adapter"
        )

        metadata = dict(
            event.get("metadata")
            or {}
        )

        metadata.update(
            {
                "adapter": self.adapter_name,
                "provider_display_name": "Nova",
            }
        )

        event["metadata"] = metadata

        return super().normalize_event(
            event,
            session_id=session_id,
            agent_id=event["agent_id"],
        )