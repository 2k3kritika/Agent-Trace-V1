from __future__ import annotations

import uuid
from typing import Any

from agenttrace_sdk.models import SDKEvent
from agenttrace_sdk.transport import AgentTraceTransport


class AgentTraceClient:
    """
    Public SDK client for instrumenting an AI agent.

    The client provides simple event helpers while keeping the underlying
    telemetry schema provider-neutral.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        agent_id: str = "local-agent",
        session_id: str | None = None,
        provider: str = "local",
        api_key: str | None = None,
        timeout: float = 10.0,
        verify: bool = True,
    ) -> None:
        self.agent_id = agent_id
        self.session_id = session_id
        self.provider = provider

        self.transport = AgentTraceTransport(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            verify=verify,
        )

    def start_session(self, session_id: str | None = None) -> str:
        self.session_id = session_id or f"sdk-{uuid.uuid4().hex[:12]}"
        return self.session_id

    def set_session(self, session_id: str | None) -> None:
        self.session_id = session_id

    def _build_event(
        self,
        event_type: str,
        *,
        status: str = "RECEIVED",
        tool: str | None = None,
        severity: str | None = None,
        details: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        parent_event_id: str | None = None,
        related_event_id: str | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
    ) -> SDKEvent:
        return SDKEvent(
            event_id=f"evt-{uuid.uuid4().hex}",
            agent_id=self.agent_id,
            session_id=self.session_id,
            provider=self.provider,
            event_type=event_type,
            status=status,
            tool=tool,
            severity=severity,
            details=details or {},
            metadata=metadata or {},
            parent_event_id=parent_event_id,
            related_event_id=related_event_id,
            trace_id=trace_id,
            span_id=span_id,
        )

    def emit(
        self,
        event_type: str,
        *,
        status: str = "RECEIVED",
        tool: str | None = None,
        severity: str | None = None,
        details: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        parent_event_id: str | None = None,
        related_event_id: str | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
    ) -> dict[str, Any]:
        event = self._build_event(
            event_type,
            status=status,
            tool=tool,
            severity=severity,
            details=details,
            metadata=metadata,
            parent_event_id=parent_event_id,
            related_event_id=related_event_id,
            trace_id=trace_id,
            span_id=span_id,
        )

        return self.transport.post(
            "/telemetry/events",
            event.as_payload(),
        )

    def emit_batch(
        self,
        events: list[SDKEvent],
    ) -> dict[str, Any]:
        return self.transport.post(
            "/telemetry/events/batch",
            {
                "events": [
                    event.as_payload()
                    for event in events
                ],
                "agent_id": self.agent_id,
                "session_id": self.session_id,
                "provider": self.provider,
            },
        )

    def user_request(
        self,
        prompt: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.emit(
            "USER_REQUEST",
            details={"prompt": prompt},
            metadata=metadata,
        )

    def agent_response(
        self,
        response: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.emit(
            "AGENT_RESPONSE",
            details={"response": response},
            metadata=metadata,
        )

    def tool_call(
        self,
        tool: str,
        arguments: dict[str, Any] | None = None,
        *,
        status: str = "REQUESTED",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.emit(
            "TOOL_CALL",
            status=status,
            tool=tool,
            details={
                "arguments": arguments or {},
            },
            metadata=metadata,
        )

    def tool_result(
        self,
        tool: str,
        result: Any,
        *,
        status: str = "SUCCEEDED",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.emit(
            "TOOL_RESULT",
            status=status,
            tool=tool,
            details={
                "result": result,
            },
            metadata=metadata,
        )

    def untrusted_content(
        self,
        content: str,
        *,
        source: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        details: dict[str, Any] = {
            "content": content,
            "trust_level": "untrusted",
        }

        if source:
            details["source"] = source

        return self.emit(
            "UNTRUSTED_CONTENT",
            severity="HIGH",
            details=details,
            metadata=metadata,
        )

    def prompt_injection_detected(
        self,
        content: str,
        *,
        indicators: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.emit(
            "PROMPT_INJECTION_DETECTED",
            status="ATTEMPTED",
            severity="HIGH",
            details={
                "content": content,
                "indicators": indicators or [],
            },
            metadata=metadata,
        )

    def sensitive_action_attempted(
        self,
        tool: str,
        *,
        arguments: dict[str, Any] | None = None,
        executed: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.emit(
            "SENSITIVE_ACTION_ATTEMPTED",
            status="ATTEMPTED",
            tool=tool,
            severity="HIGH",
            details={
                "arguments": arguments or {},
                "sensitive_action": True,
                "executed": executed,
            },
            metadata=metadata,
        )

    def policy_violation(
        self,
        *,
        policy: str,
        reason: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.emit(
            "POLICY_VIOLATION",
            status="BLOCKED",
            severity="HIGH",
            details={
                "policy": policy,
                "reason": reason,
            },
            metadata=metadata,
        )

    def tool_blocked(
        self,
        tool: str,
        *,
        reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.emit(
            "TOOL_BLOCKED",
            status="BLOCKED",
            tool=tool,
            severity="HIGH",
            details={
                "reason": reason,
                "blocked": True,
            },
            metadata=metadata,
        )

    def health(self) -> dict[str, Any]:
        return self.transport.health()