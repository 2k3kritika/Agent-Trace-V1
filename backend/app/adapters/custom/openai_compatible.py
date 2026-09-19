from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from app.adapters.base import AdapterConnectionResult, AdapterHealthResult, AgentAdapter
from app.domain.events.models import CanonicalEvent
from app.domain.events.normalizer import EventNormalizer


class OpenAICompatibleAdapter(AgentAdapter):
    """
    Adapter for OpenAI-style and OpenAI-compatible agent telemetry.

    The adapter intentionally accepts plain dictionaries instead of importing
    an OpenAI client SDK. This makes it usable with OpenAI-compatible providers,
    local models, proxies, and custom agent frameworks.
    """

    name = "openai_compatible"
    provider = "openai_compatible"
    display_name = "OpenAI Compatible"
    adapter_name = "openai_compatible"

    _EVENT_TYPE_ALIASES: ClassVar[dict[str, str]] = {
        "request": "USER_REQUEST",
        "user_request": "USER_REQUEST",
        "prompt": "USER_REQUEST",
        "response": "AGENT_RESPONSE",
        "assistant_response": "AGENT_RESPONSE",
        "chat_completion": "AGENT_RESPONSE",
        "tool_call": "TOOL_CALL",
        "function_call": "TOOL_CALL",
        "tool_result": "TOOL_RESULT",
        "function_result": "TOOL_RESULT",
        "content_retrieved": "CONTENT_RETRIEVED",
        "retrieval": "CONTENT_RETRIEVED",
        "untrusted_content": "UNTRUSTED_CONTENT",
        "prompt_injection": "PROMPT_INJECTION_DETECTED",
        "prompt_injection_detected": "PROMPT_INJECTION_DETECTED",
        "sensitive_action": "SENSITIVE_ACTION_ATTEMPTED",
        "sensitive_action_attempted": "SENSITIVE_ACTION_ATTEMPTED",
        "policy_violation": "POLICY_VIOLATION",
        "tool_blocked": "TOOL_BLOCKED",
        "tool_allowed": "TOOL_ALLOWED",
        "error": "ERROR",
    }

    def __init__(self, normalizer: EventNormalizer | None = None) -> None:
        self.normalizer = normalizer or EventNormalizer()

    def _event_type(self, value: Any) -> str:
        normalized = str(value or "AGENT_RESPONSE").strip().lower()

        return self._EVENT_TYPE_ALIASES.get(
            normalized,
            str(value).upper() if value else "AGENT_RESPONSE",
        )

    def _extract_tool(self, payload: Mapping[str, Any]) -> str | None:
        direct_tool = payload.get("tool") or payload.get("tool_name")

        if direct_tool:
            return str(direct_tool)

        tool_calls = payload.get("tool_calls")

        if isinstance(tool_calls, list) and tool_calls:
            first = tool_calls[0]

            if isinstance(first, Mapping):
                function = first.get("function")

                if isinstance(function, Mapping):
                    name = function.get("name")
                    if name:
                        return str(name)

                name = first.get("name")
                if name:
                    return str(name)

        function_call = payload.get("function_call")

        if isinstance(function_call, Mapping):
            name = function_call.get("name")
            if name:
                return str(name)

        return None

    def normalize_event(
        self,
        raw_event: Mapping[str, Any],
        *,
        default_agent_id: str | None = None,
        default_session_id: str | None = None,
    ) -> CanonicalEvent:
        payload = dict(raw_event)

        event_type = self._event_type(
            payload.get("event_type") or payload.get("type") or payload.get("event")
        )

        details = dict(payload.get("details") or {})

        for key in (
            "messages",
            "prompt",
            "response",
            "content",
            "tool_calls",
            "function_call",
            "arguments",
            "result",
            "error",
        ):
            if key in payload:
                details.setdefault(key, payload[key])

        tool = self._extract_tool(payload)

        model = payload.get("model") or payload.get("model_name")

        canonical_payload = {
            "event_id": payload.get("event_id") or payload.get("id"),
            "timestamp": payload.get("timestamp") or payload.get("created_at"),
            "session_id": payload.get("session_id") or default_session_id,
            "agent_id": payload.get("agent_id") or default_agent_id,
            "provider": "openai_compatible",
            "event_type": event_type,
            "status": payload.get("status") or "RECEIVED",
            "tool": tool,
            "source": "openai_compatible_adapter",
            "severity": payload.get("severity"),
            "details": details,
            "metadata": {
                **dict(payload.get("metadata") or {}),
                "adapter": self.name,
                "provider_display_name": self.display_name,
                "model": model,
                "finish_reason": payload.get("finish_reason"),
            },
            "parent_event_id": payload.get("parent_event_id"),
            "related_event_id": payload.get("related_event_id"),
            "trace_id": payload.get("trace_id"),
            "span_id": payload.get("span_id"),
        }

        canonical_payload["metadata"] = {
            key: value
            for key, value in canonical_payload["metadata"].items()
            if value is not None
        }

        return self.normalizer.normalize(
            canonical_payload,
            default_agent_id=default_agent_id,
            default_session_id=default_session_id,
            default_provider="openai_compatible",
        )

    def validate_connection(
        self, configuration: Mapping[str, Any] | None = None
    ) -> AdapterConnectionResult:
        configuration = configuration or {}

        endpoint = configuration.get("endpoint") or configuration.get("base_url")

        return AdapterConnectionResult(
            success=True,
            adapter=self.name,
            provider=self.provider,
            message=(
                f"OpenAI-compatible adapter configured for {endpoint}."
                if endpoint
                else "OpenAI-compatible adapter is ready for telemetry normalization."
            ),
        )

    def health_check(self) -> AdapterHealthResult:
        return AdapterHealthResult(
            healthy=True,
            adapter=self.name,
            provider=self.provider,
            message="OpenAI-compatible adapter is ready.",
        )
