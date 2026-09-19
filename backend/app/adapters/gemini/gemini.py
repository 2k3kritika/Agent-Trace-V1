from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.adapters.base import AgentAdapter, AdapterConnectionResult, AdapterHealthResult
from app.domain.events.models import CanonicalEvent
from app.domain.events.normalizer import EventNormalizer


class GeminiAdapter(AgentAdapter):
    """
    Adapter for Google Gemini-style telemetry.

    This adapter deliberately does not depend on the Google Gemini SDK.
    It accepts already-captured telemetry dictionaries so AgentTrace remains
    provider-neutral and can operate with local wrappers, application logs,
    middleware, or future Gemini SDK integrations.
    """

    name = "gemini"
    adapter_name = "gemini"
    provider = "google_gemini"
    display_name = "Google Gemini"

    _EVENT_TYPE_ALIASES = {
        "request": "USER_REQUEST",
        "user_request": "USER_REQUEST",
        "prompt": "USER_REQUEST",
        "response": "AGENT_RESPONSE",
        "model_response": "AGENT_RESPONSE",
        "tool_call": "TOOL_CALL",
        "function_call": "TOOL_CALL",
        "functioncall": "TOOL_CALL",
        "tool_result": "TOOL_RESULT",
        "function_response": "TOOL_RESULT",
        "functionresponse": "TOOL_RESULT",
        "retrieved_content": "CONTENT_RETRIEVED",
        "content_retrieved": "CONTENT_RETRIEVED",
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

    def _string(self, value: Any, default: str | None = None) -> str | None:
        if value is None:
            return default
        return str(value)

    def _event_type(self, value: Any) -> str:
        normalized = str(value or "AGENT_RESPONSE").strip().lower()
        return self._EVENT_TYPE_ALIASES.get(
            normalized,
            str(value).upper() if value else "AGENT_RESPONSE",
        )

    def _extract_tool(self, payload: Mapping[str, Any]) -> str | None:
        tool = payload.get("tool") or payload.get("tool_name")

        if tool:
            return str(tool)

        function_call = payload.get("function_call")

        if isinstance(function_call, Mapping):
            name = function_call.get("name")
            if name:
                return str(name)

        function_calls = payload.get("function_calls")

        if isinstance(function_calls, list) and function_calls:
            first = function_calls[0]
            if isinstance(first, Mapping):
                name = first.get("name")
                if name:
                    return str(name)

                function = first.get("function")
                if isinstance(function, Mapping) and function.get("name"):
                    return str(function["name"])

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
            payload.get("event_type")
            or payload.get("type")
            or payload.get("event")
        )

        details = dict(payload.get("details") or {})

        if "prompt" in payload:
            details.setdefault("prompt", payload["prompt"])

        if "response" in payload:
            details.setdefault("response", payload["response"])

        if "text" in payload:
            details.setdefault("text", payload["text"])

        if "parts" in payload:
            details.setdefault("parts", payload["parts"])

        if "function_call" in payload:
            details.setdefault("function_call", payload["function_call"])

        if "function_response" in payload:
            details.setdefault("function_response", payload["function_response"])

        if "tool_result" in payload:
            details.setdefault("tool_result", payload["tool_result"])

        tool = self._extract_tool(payload)

        canonical_payload = {
            "event_id": payload.get("event_id") or payload.get("id"),
            "timestamp": payload.get("timestamp") or payload.get("created_at"),
            "session_id": payload.get("session_id") or default_session_id,
            "agent_id": payload.get("agent_id") or default_agent_id,
            "provider": "google_gemini",
            "event_type": event_type,
            "status": payload.get("status") or "RECEIVED",
            "tool": tool,
            "source": "gemini_adapter",
            "severity": payload.get("severity"),
            "details": details,
            "metadata": {
                **dict(payload.get("metadata") or {}),
                "adapter": self.name,
                "provider_display_name": self.display_name,
                "model": payload.get("model"),
                "model_name": payload.get("model_name"),
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
            default_provider="google_gemini",
        )

    def validate_connection(self, configuration: Mapping[str, Any] | None = None) -> AdapterConnectionResult:
        configuration = configuration or {}

        if configuration.get("api_key") or configuration.get("api_key_reference"):
            return AdapterConnectionResult(
                success=True,
                adapter=self.name,
                provider=self.provider,
                message="Gemini adapter configuration is present.",
            )

        return AdapterConnectionResult(
            success=True,
            adapter=self.name,
            provider=self.provider,
            message=(
                "Gemini adapter is available for telemetry normalization. "
                "No API key is required for adapter-only operation."
            ),
        )

    def health_check(self) -> AdapterHealthResult:
        return AdapterHealthResult(
            healthy=True,
            adapter=self.name,
            provider=self.provider,
            message="Gemini adapter is ready.",
        )