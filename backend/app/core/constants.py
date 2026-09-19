"""Application-wide constants and enumerations.

This module contains values shared across the domain, API, persistence,
and infrastructure layers. Security-sensitive business decisions should
not be implemented here.
"""

from enum import StrEnum


class Environment(StrEnum):
    """Supported application environments."""

    LOCAL = "local"
    TEST = "test"
    AWS = "aws"


class StorageBackend(StrEnum):
    """Supported persistence backends."""

    POSTGRES = "postgres"
    DYNAMODB = "dynamodb"


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
    """Canonical event processing statuses."""

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


class Severity(StrEnum):
    """Security severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskLevel(StrEnum):
    """Risk classification derived from deterministic scoring."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AgentStatus(StrEnum):
    """Current monitored-agent status."""

    ONLINE = "ONLINE"
    IDLE = "IDLE"
    OFFLINE = "OFFLINE"


class SessionStatus(StrEnum):
    """Agent session lifecycle states."""

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class InvestigationStatus(StrEnum):
    """Investigation lifecycle states."""

    OPEN = "OPEN"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"


class AlertStatus(StrEnum):
    """Alert lifecycle states."""

    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class PolicyDecision(StrEnum):
    """Possible deterministic policy outcomes."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    SIMULATE = "SIMULATE"


class IntegrationType(StrEnum):
    """Supported integration categories."""

    LOCAL_AGENT = "LOCAL_AGENT"
    GEMINI = "GEMINI"
    OPENAI_COMPATIBLE = "OPENAI_COMPATIBLE"
    AGENTTRACE_SDK = "AGENTTRACE_SDK"


class IntegrationStatus(StrEnum):
    """Integration connection states."""

    CONNECTING = "CONNECTING"
    RECEIVING_TEST_EVENT = "RECEIVING_TEST_EVENT"
    NORMALIZING_TELEMETRY = "NORMALIZING_TELEMETRY"
    CONNECTED = "CONNECTED"
    FAILED = "FAILED"


class EvidenceType(StrEnum):
    """Types of forensic evidence."""

    EVENT = "EVENT"
    EVENT_SEQUENCE = "EVENT_SEQUENCE"
    RAW_TELEMETRY = "RAW_TELEMETRY"
    RETRIEVED_CONTENT = "RETRIEVED_CONTENT"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    POLICY_DECISION = "POLICY_DECISION"
    CAPTURED_ARTIFACT = "CAPTURED_ARTIFACT"
    REPORT = "REPORT"
    MAILBOX_ARTIFACT = "MAILBOX_ARTIFACT"


class VerdictType(StrEnum):
    """High-level forensic verdicts."""

    POLICY_VIOLATION = "POLICY_VIOLATION"
    SUSPICIOUS_BEHAVIOR = "SUSPICIOUS_BEHAVIOR"
    BENIGN = "BENIGN"
    UNDETERMINED = "UNDETERMINED"


class GraphNodeState(StrEnum):
    """Visual state consumed by the frontend graph."""

    NORMAL = "normal"
    WARNING = "warning"
    DANGER = "danger"
    BLOCKED = "blocked"
    SUCCESS = "success"


class GraphRelationship(StrEnum):
    """Relationships between attack-graph nodes."""

    CAUSED = "CAUSED"
    FOLLOWED = "FOLLOWED"
    RELATED = "RELATED"
    BLOCKED = "BLOCKED"


class Provider(StrEnum):
    """Known telemetry providers."""

    LOCAL = "local"
    GEMINI = "gemini"
    CUSTOM = "custom"


class SensitiveAction(StrEnum):
    """Sensitive actions recognized by AgentTrace."""

    SEND_EMAIL = "send_email"
    SEND_MESSAGE = "send_message"
    DELETE_DATA = "delete_data"
    MODIFY_ACCOUNT = "modify_account"
    EXECUTE_CODE = "execute_code"
    ACCESS_SECRET = "access_secret"
    EXTERNAL_HTTP_REQUEST = "external_http_request"
    DATABASE_WRITE = "database_write"
    FINANCIAL_ACTION = "financial_action"


# Deterministic risk signals specified by the AgentTrace implementation plan.
RISK_SIGNAL_PROMPT_INJECTION = 30
RISK_SIGNAL_UNTRUSTED_CONTENT = 10
RISK_SIGNAL_SENSITIVE_ACTION_ATTEMPTED = 25
RISK_SIGNAL_POLICY_VIOLATION = 20
RISK_SIGNAL_SENSITIVE_ACTION_EXECUTED = 30
RISK_SIGNAL_EXTERNAL_TRANSMISSION = 40
RISK_SIGNAL_BLOCKED_ACTION = -10

RISK_MIN = 0
RISK_MAX = 100

RISK_LOW_MAX = 24
RISK_MEDIUM_MAX = 49
RISK_HIGH_MAX = 74

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100

DEFAULT_EVENT_PAGE_SIZE = 50
MAX_EVENT_PAGE_SIZE = 250

REQUEST_ID_HEADER = "X-Request-ID"

API_V1_PREFIX = "/api/v1"

APP_NAME = "AgentTrace"

HEALTH_PATH = "/health"
API_HEALTH_PATH = f"{API_V1_PREFIX}/health"

DEFAULT_PROVIDER_DISPLAY_NAMES: dict[str, str] = {
    Provider.LOCAL.value: "Local Python Agent",
    Provider.GEMINI.value: "Google Gemini",
    Provider.CUSTOM.value: "Custom Provider",
}

SENSITIVE_ACTION_VALUES = {action.value for action in SensitiveAction}
