from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.postgres.database import get_db_session
from app.infrastructure.storage.local import LocalArtifactStorage
from app.repositories.postgres.agent import PostgresAgentRepository
from app.repositories.postgres.alert import PostgresAlertRepository
from app.repositories.postgres.dashboard import PostgresDashboardRepository
from app.repositories.postgres.event import PostgresEventRepository
from app.repositories.postgres.evidence import PostgresEvidenceRepository
from app.repositories.postgres.integration import (
    PostgresIntegrationRepository,
)
from app.repositories.postgres.investigation import (
    PostgresInvestigationRepository,
)
from app.repositories.postgres.policy import PostgresPolicyRepository
from app.repositories.postgres.report import PostgresReportRepository
from app.repositories.postgres.session import PostgresSessionRepository
from app.repositories.postgres.user import PostgresUserRepository
from app.services.agent_service import AgentService
from app.services.alert_service import AlertService
from app.services.artifact_service import ArtifactService
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService
from app.services.detection_service import DetectionService
from app.services.event_service import EventService
from app.services.evidence_service import EvidenceService
from app.services.forensic_service import ForensicService
from app.services.integration_service import IntegrationService
from app.services.investigation_forensic_service import (
    InvestigationForensicService,
)
from app.services.investigation_service import InvestigationService
from app.services.policy_service import PolicyService
from app.services.report_service import ReportService
from app.services.session_service import SessionService
from app.services.telemetry_service import TelemetryService


def get_agent_service(
    db: AsyncSession = Depends(get_db_session),
) -> AgentService:
    repository = PostgresAgentRepository(db)
    return AgentService(repository)


def get_alert_service(
    db: AsyncSession = Depends(get_db_session),
) -> AlertService:
    repository = PostgresAlertRepository(db)
    return AlertService(repository)


def get_event_service(
    db: AsyncSession = Depends(get_db_session),
) -> EventService:
    repository = PostgresEventRepository(db)
    return EventService(repository)


def get_evidence_service(
    db: AsyncSession = Depends(get_db_session),
) -> EvidenceService:
    repository = PostgresEvidenceRepository(db)
    return EvidenceService(repository)


def get_report_service(
    db: AsyncSession = Depends(get_db_session),
) -> ReportService:
    repository = PostgresReportRepository(db)
    return ReportService(repository)


def get_forensic_service() -> ForensicService:
    return ForensicService()


def get_detection_service() -> DetectionService:
    return DetectionService()


def get_investigation_service(
    db: AsyncSession = Depends(get_db_session),
) -> InvestigationService:
    repository = PostgresInvestigationRepository(db)
    return InvestigationService(repository)


def get_integration_service(
    db: AsyncSession = Depends(get_db_session),
) -> IntegrationService:
    repository = PostgresIntegrationRepository(db)
    return IntegrationService(repository)


def get_policy_service(
    db: AsyncSession = Depends(get_db_session),
) -> PolicyService:
    repository = PostgresPolicyRepository(db)
    return PolicyService(repository)


def get_session_service(
    db: AsyncSession = Depends(get_db_session),
) -> SessionService:
    repository = PostgresSessionRepository(db)
    return SessionService(repository)


def get_telemetry_service(
    db: AsyncSession = Depends(get_db_session),
) -> TelemetryService:
    event_repository = PostgresEventRepository(db)
    event_service = EventService(event_repository)

    return TelemetryService(event_service)


def get_investigation_forensic_service(
    db: AsyncSession = Depends(get_db_session),
) -> InvestigationForensicService:
    investigation_service = InvestigationService(PostgresInvestigationRepository(db))

    event_service = EventService(PostgresEventRepository(db))

    evidence_service = EvidenceService(PostgresEvidenceRepository(db))

    forensic_service = ForensicService()

    return InvestigationForensicService(
        investigation_service=investigation_service,
        event_service=event_service,
        evidence_service=evidence_service,
        forensic_service=forensic_service,
    )


def get_dashboard_repository(
    db: AsyncSession = Depends(get_db_session),
) -> PostgresDashboardRepository:
    return PostgresDashboardRepository(db)


def get_dashboard_service(
    repository: PostgresDashboardRepository = Depends(get_dashboard_repository),
) -> DashboardService:
    return DashboardService(repository)


def get_artifact_storage() -> LocalArtifactStorage:
    return LocalArtifactStorage()


def get_artifact_service(
    storage: LocalArtifactStorage = Depends(get_artifact_storage),
) -> ArtifactService:
    return ArtifactService(storage)


def get_user_repository(
    db: AsyncSession = Depends(get_db_session),
) -> PostgresUserRepository:
    return PostgresUserRepository(db)


def get_auth_service(
    repository: PostgresUserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository)


def get_event_repository(
    db: AsyncSession = Depends(get_db_session),
) -> PostgresEventRepository:
    return PostgresEventRepository(db)


def get_audit_service(
    repository: PostgresEventRepository = Depends(get_event_repository),
) -> AuditService:
    return AuditService(repository)
