"""
Domain-level event type definitions.

These values describe AgentTrace semantics rather than any specific
provider or framework.
"""

from __future__ import annotations

from enum import StrEnum


class EventType(StrEnum):
    """Canonical AgentTrace event types."""

    AGENT_STARTED = "AGENT_STARTED"
    AGENT_COMPLETED = "AGENT_COMPLETED"

    USER_REQUEST = "USER_REQUEST"
    AGENT_RESPONSE = "AGENT_RESPONSE"
    AGENT_DECISION = "AGENT_DECISION"

    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"

    CONTENT_RETRIEVED = "CONTENT_RETRIEVED"
    UNTRUSTED_CONTENT = "UNTRUSTED_CONTENT"

    PROMPT_INJECTION_DETECTED = "PROMPT_INJECTION_DETECTED"

    SENSITIVE_ACTION_ATTEMPTED = "SENSITIVE_ACTION_ATTEMPTED"

    POLICY_EVALUATION = "POLICY_EVALUATION"
    POLICY_VIOLATION = "POLICY_VIOLATION"

    TOOL_BLOCKED = "TOOL_BLOCKED"
    TOOL_ALLOWED = "TOOL_ALLOWED"

    ERROR = "ERROR"


class EventStatus(StrEnum):
    """Canonical processing/execution status values."""

    RECEIVED = "RECEIVED"
    REQUESTED = "REQUESTED"
    STARTED = "STARTED"

    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

    ATTEMPTED = "ATTEMPTED"
    BLOCKED = "BLOCKED"
    ALLOWED = "ALLOWED"

    SIMULATED = "SIMULATED"
    COMPLETED = "COMPLETED"


class EventSeverity(StrEnum):
    """Severity associated with a canonical event."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EventRelationshipType(StrEnum):
    """Supported event-to-event relationship types."""

    PARENT = "PARENT"
    RELATED = "RELATED"
    CAUSED_BY = "CAUSED_BY"
    FOLLOWS = "FOLLOWS"
    DERIVED_FROM = "DERIVED_FROM"