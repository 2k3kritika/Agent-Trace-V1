"""Application exception hierarchy and API error helpers."""

from typing import Any


class AgentTraceError(Exception):
    """Base exception for expected AgentTrace application errors."""

    code = "AGENTTRACE_ERROR"
    status_code = 500
    default_message = "An AgentTrace error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.details = details or {}

        super().__init__(self.message)

class RepositoryError(AgentTraceError):
    """Raised when a repository operation fails."""

class ValidationError(AgentTraceError):
    """Raised when domain-level validation fails."""

    code = "VALIDATION_ERROR"
    status_code = 422
    default_message = "The supplied data is invalid."


class AuthenticationError(AgentTraceError):
    """Raised when authentication fails."""

    code = "AUTHENTICATION_ERROR"
    status_code = 401
    default_message = "Authentication is required."


class AuthorizationError(AgentTraceError):
    """Raised when an authenticated actor lacks permission."""

    code = "AUTHORIZATION_ERROR"
    status_code = 403
    default_message = "You are not authorized to perform this action."

class NotFoundError(AgentTraceError):
    """Raised when a requested resource does not exist."""


class DuplicateResourceError(AgentTraceError):
    """Raised when a resource already exists."""


class ResourceNotFoundError(AgentTraceError):
    """Base exception for missing resources."""

    code = "RESOURCE_NOT_FOUND"
    status_code = 404
    default_message = "The requested resource was not found."


class AgentNotFoundError(ResourceNotFoundError):
    """Raised when an agent cannot be found."""

    code = "AGENT_NOT_FOUND"
    default_message = "Agent was not found."


class IntegrationNotFoundError(ResourceNotFoundError):
    """Raised when an integration cannot be found."""

    code = "INTEGRATION_NOT_FOUND"
    default_message = "Integration was not found."


class SessionNotFoundError(ResourceNotFoundError):
    """Raised when a session cannot be found."""

    code = "SESSION_NOT_FOUND"
    default_message = "Session was not found."


class EventNotFoundError(ResourceNotFoundError):
    """Raised when an event cannot be found."""

    code = "EVENT_NOT_FOUND"
    default_message = "Event was not found."


class InvestigationNotFoundError(ResourceNotFoundError):
    """Raised when an investigation cannot be found."""

    code = "INVESTIGATION_NOT_FOUND"
    default_message = "Investigation was not found."


class AlertNotFoundError(ResourceNotFoundError):
    """Raised when an alert cannot be found."""

    code = "ALERT_NOT_FOUND"
    default_message = "Alert was not found."


class EvidenceNotFoundError(ResourceNotFoundError):
    """Raised when evidence cannot be found."""

    code = "EVIDENCE_NOT_FOUND"
    default_message = "Evidence was not found."


class PolicyNotFoundError(ResourceNotFoundError):
    """Raised when a policy cannot be found."""

    code = "POLICY_NOT_FOUND"
    default_message = "Policy was not found."


class ReportNotFoundError(ResourceNotFoundError):
    """Raised when a report cannot be found."""

    code = "REPORT_NOT_FOUND"
    default_message = "Report was not found."


class ArtifactNotFoundError(ResourceNotFoundError):
    """Raised when an artifact cannot be found."""

    code = "ARTIFACT_NOT_FOUND"
    default_message = "Artifact was not found."


class ConflictError(AgentTraceError):
    """Raised when an operation conflicts with existing state."""

    code = "CONFLICT"
    status_code = 409
    default_message = "The requested operation conflicts with existing state."


class DuplicateEventError(ConflictError):
    """Raised when telemetry violates event idempotency."""

    code = "DUPLICATE_EVENT"
    default_message = "This telemetry event has already been processed."


class IntegrationError(AgentTraceError):
    """Raised when an adapter/integration operation fails."""

    code = "INTEGRATION_ERROR"
    status_code = 502
    default_message = "The integration operation failed."


class StorageError(AgentTraceError):
    """Raised when persistence or object storage fails."""

    code = "STORAGE_ERROR"
    status_code = 500
    default_message = "A storage operation failed."


class ConfigurationError(AgentTraceError):
    """Raised for invalid runtime configuration."""

    code = "CONFIGURATION_ERROR"
    status_code = 500
    default_message = "The application configuration is invalid."


def error_payload(
    *,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    """Build the standard AgentTrace API error envelope."""

    payload: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }

    if request_id:
        payload["request_id"] = request_id

    return payload

class AppError(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "APPLICATION_ERROR",
        status_code: int = 400,
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}