from __future__ import annotations

from typing import Any, ClassVar

from app.adapters.local.generic import GenericLocalAdapter
from app.domain.events.models import CanonicalEvent


class ResearchAgentAdapter(GenericLocalAdapter):
    """
    Adapter for the existing Research Agent.

    The Research Agent is not rebuilt here. Its telemetry is
    consumed and translated into AgentTrace's canonical event
    model.

    The adapter preserves:
        parent_event_id
        related_event_id
        trace_id
        span_id

    so the investigation/correlation layer can reconstruct
    the attack chain.
    """

    adapter_name = "research"
    provider_name = "local"

    _EVENT_ALIASES: ClassVar[dict[str, str]] = {
        "agent_started": "AGENT_STARTED",
        "started": "AGENT_STARTED",
        "user_request": "USER_REQUEST",
        "user_message": "USER_REQUEST",
        "request": "USER_REQUEST",
        "tool_call": "TOOL_CALL",
        "tool_invocation": "TOOL_CALL",
        "search": "TOOL_CALL",
        "web_search": "TOOL_CALL",
        "fetch": "TOOL_CALL",
        "tool_result": "TOOL_RESULT",
        "tool_response": "TOOL_RESULT",
        "content_retrieved": "CONTENT_RETRIEVED",
        "retrieved_content": "CONTENT_RETRIEVED",
        "external_content": "CONTENT_RETRIEVED",
        "untrusted_content": "UNTRUSTED_CONTENT",
        "untrusted": "UNTRUSTED_CONTENT",
        "prompt_injection_detected": ("PROMPT_INJECTION_DETECTED"),
        "prompt_injection": ("PROMPT_INJECTION_DETECTED"),
        "agent_decision": "AGENT_DECISION",
        "decision": "AGENT_DECISION",
        "sensitive_action_attempted": ("SENSITIVE_ACTION_ATTEMPTED"),
        "sensitive_action": ("SENSITIVE_ACTION_ATTEMPTED"),
        "tool_simulated": "TOOL_RESULT",
        "simulated_tool_result": "TOOL_RESULT",
        "agent_completed": "AGENT_COMPLETED",
        "completed": "AGENT_COMPLETED",
        "error": "ERROR",
    }

    _STATUS_ALIASES: ClassVar[dict[str, str]] = {
        "received": "RECEIVED",
        "requested": "REQUESTED",
        "started": "STARTED",
        "succeeded": "SUCCEEDED",
        "success": "SUCCEEDED",
        "failed": "FAILED",
        "failure": "FAILED",
        "attempted": "ATTEMPTED",
        "blocked": "BLOCKED",
        "allowed": "ALLOWED",
        "simulated": "SIMULATED",
        "completed": "COMPLETED",
    }

    def normalize_event(
        self,
        raw_event: dict[str, Any],
        *,
        session_id: str | None = None,
        agent_id: str | None = "research-agent",
    ) -> CanonicalEvent:
        event = dict(raw_event)

        raw_type = str(
            event.get("event_type") or event.get("type") or event.get("name") or ""
        ).strip()

        canonical_type = self._EVENT_ALIASES.get(
            raw_type.lower(),
            raw_type.upper(),
        )

        event["event_type"] = canonical_type

        raw_status = str(event.get("status") or "RECEIVED").strip()

        event["status"] = self._STATUS_ALIASES.get(
            raw_status.lower(),
            raw_status.upper(),
        )

        event["agent_id"] = event.get("agent_id") or agent_id or "research-agent"

        event["provider"] = "local"

        event["source"] = event.get("source") or "research_agent_adapter"

        details = dict(event.get("details") or {})

        metadata = dict(event.get("metadata") or {})

        metadata.update(
            {
                "adapter": self.adapter_name,
                "provider_display_name": ("Local Python Research Agent"),
            }
        )

        # Preserve attack-chain relationships if the source
        # telemetry uses any of these common aliases.
        for field in (
            "parent_event_id",
            "related_event_id",
            "trace_id",
            "span_id",
        ):
            if event.get(field) is None:
                alias_value = event.get(
                    {
                        "parent_event_id": "parent_id",
                        "related_event_id": "related_id",
                        "trace_id": "trace",
                        "span_id": "span",
                    }[field]
                )

                if alias_value is not None:
                    event[field] = alias_value

        # Preserve useful research-agent context without
        # changing the canonical event contract.
        if "url" in event and "url" not in details:
            details["url"] = event["url"]

        if "content" in event and "content" not in details:
            details["content"] = event["content"]

        if "query" in event and "query" not in details:
            details["query"] = event["query"]

        event["details"] = details
        event["metadata"] = metadata

        return super().normalize_event(
            event,
            session_id=session_id,
            agent_id=event["agent_id"],
        )
