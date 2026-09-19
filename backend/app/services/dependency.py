from __future__ import annotations

from typing import Any

from fastapi import Depends

from app.infrastructure.storage.factory import create_artifact_storage

from app.repositories.provider import (
    get_agent_repository,
    get_alert_repository,
    get_evidence_repository,
    get_event_repository,
    get_integration_repository,
    get_investigation_repository,
    get_policy_repository,
    get_report_repository,
    get_session_repository,
    get_user_repository,
)

from app.services.adapter_service import AdapterService
from app.services.agent_service import AgentService
from app.services.alert_service import AlertService
from app.services.artifact_service import ArtifactService
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.correlation_service import CorrelationService
from app.services.dashboard_service import DashboardService
from app.services.demo_scenario_service import DemoScenarioService
from app.services.detection_service import DetectionService
from app.services.evidence_service import EvidenceService
from app.services.event_service import EventService
from app.services.forensic_service import ForensicService
from app.services.integration_service import IntegrationService
from app.services.investigation_forensic_service import (
    InvestigationForensicService,
)
from app.services.investigation_service import InvestigationService
from app.services.policy_service import PolicyService
from app.services.report_service import ReportService
from app.services.risk_service import RiskService
from app.services.session_service import SessionService
from app.services.storage_service import StorageService
from app.services.telemetry_service import TelemetryService


# ---------------------------------------------------------------------------
# Repository-backed services
# ---------------------------------------------------------------------------


def get_agent_service(
    repository: Any = Depends(get_agent_repository),
) -> AgentService:
    return AgentService(repository)


def get_event_service(
    repository: Any = Depends(get_event_repository),
) -> EventService:
    return EventService(repository)


def get_session_service(
    repository: Any = Depends(get_session_repository),
) -> SessionService:
    return SessionService(repository)


def get_investigation_service(
    repository: Any = Depends(get_investigation_repository),
) -> InvestigationService:
    return InvestigationService(repository)


def get_alert_service(
    repository: Any = Depends(get_alert_repository),
) -> AlertService:
    return AlertService(repository)


def get_evidence_service(
    repository: Any = Depends(get_evidence_repository),
) -> EvidenceService:
    return EvidenceService(repository)


def get_integration_service(
    repository: Any = Depends(get_integration_repository),
) -> IntegrationService:
    return IntegrationService(repository)


def get_report_service(
    repository: Any = Depends(get_report_repository),
) -> ReportService:
    return ReportService(repository)


def get_auth_service(
    repository: Any = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository)


# ---------------------------------------------------------------------------
# Stateless services
# ---------------------------------------------------------------------------


def get_detection_service() -> DetectionService:
    return DetectionService()


def get_policy_service() -> PolicyService:
    return PolicyService()


def get_risk_service() -> RiskService:
    return RiskService()


def get_forensic_service() -> ForensicService:
    return ForensicService()


def get_correlation_service() -> CorrelationService:
    return CorrelationService()


# ---------------------------------------------------------------------------
# Event-dependent services
# ---------------------------------------------------------------------------


def get_adapter_service(
    event_service: EventService = Depends(get_event_service),
) -> AdapterService:
    return AdapterService(event_service)


def get_telemetry_service(
    event_service: EventService = Depends(get_event_service),
) -> TelemetryService:
    return TelemetryService(event_service)


def get_audit_service(
    event_repository: Any = Depends(get_event_repository),
) -> AuditService:
    return AuditService(event_repository)


# ---------------------------------------------------------------------------
# Artifact / storage services
# ---------------------------------------------------------------------------
def get_storage_service() -> StorageService:
    storage = create_artifact_storage()
    return StorageService(storage)


def get_artifact_service(
    storage_service: StorageService = Depends(get_storage_service),
) -> ArtifactService:
    return ArtifactService(storage_service)


# ---------------------------------------------------------------------------
# Dashboard service
# ---------------------------------------------------------------------------


def get_dashboard_service(
    agent_repository: Any = Depends(get_agent_repository),
    session_repository: Any = Depends(get_session_repository),
    investigation_repository: Any = Depends(get_investigation_repository),
    alert_repository: Any = Depends(get_alert_repository),
    event_repository: Any = Depends(get_event_repository),
) -> DashboardService:
    return DashboardService(
        agent_repository=agent_repository,
        session_repository=session_repository,
        investigation_repository=investigation_repository,
        alert_repository=alert_repository,
        event_repository=event_repository,
    )


# ---------------------------------------------------------------------------
# Investigation forensic service
# ---------------------------------------------------------------------------


def get_investigation_forensic_service(
    investigation_service: InvestigationService = Depends(
        get_investigation_service
    ),
    event_service: EventService = Depends(get_event_service),
    evidence_service: EvidenceService = Depends(get_evidence_service),
    forensic_service: ForensicService = Depends(get_forensic_service),
) -> InvestigationForensicService:
    return InvestigationForensicService(
        investigation_service=investigation_service,
        event_service=event_service,
        evidence_service=evidence_service,
        forensic_service=forensic_service,
    )


# ---------------------------------------------------------------------------
# Demo scenario service
# ---------------------------------------------------------------------------


def get_demo_scenario_service(
    event_service: EventService = Depends(get_event_service),
    detection_service: DetectionService = Depends(get_detection_service),
    policy_service: PolicyService = Depends(get_policy_service),
    risk_service: RiskService = Depends(get_risk_service),
    investigation_service: InvestigationService = Depends(
        get_investigation_service
    ),
    forensic_service: ForensicService = Depends(get_forensic_service),
) -> DemoScenarioService:
    return DemoScenarioService(
        event_service=event_service,
        detection_service=detection_service,
        policy_service=policy_service,
        risk_service=risk_service,
        investigation_service=investigation_service,
        forensic_service=forensic_service,
    )