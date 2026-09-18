from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.postgres.database import AsyncSessionFactory
from app.repositories.postgres.agent import PostgresAgentRepository
from app.repositories.postgres.alert import PostgresAlertRepository
from app.repositories.postgres.evidence import PostgresEvidenceRepository
from app.repositories.postgres.event import PostgresEventRepository
from app.repositories.postgres.integration import PostgresIntegrationRepository
from app.repositories.postgres.investigation import (
    PostgresInvestigationRepository,
)
from app.repositories.postgres.session import PostgresSessionRepository
from app.services.agent_service import AgentService
from app.services.alert_service import AlertService
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
from app.services.risk_service import RiskService
from app.services.session_service import SessionService
from app.services.telemetry_service import TelemetryService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session


def get_agent_service(
    db: AsyncSession = Depends(get_db_session),
) -> AgentService:
    return AgentService(PostgresAgentRepository(db))


def get_alert_service(
    db: AsyncSession = Depends(get_db_session),
) -> AlertService:
    return AlertService(PostgresAlertRepository(db))


def get_detection_service() -> DetectionService:
    return DetectionService()


def get_evidence_service(
    db: AsyncSession = Depends(get_db_session),
) -> EvidenceService:
    return EvidenceService(PostgresEvidenceRepository(db))


def get_event_service(
    db: AsyncSession = Depends(get_db_session),
) -> EventService:
    return EventService(PostgresEventRepository(db))


def get_forensic_service() -> ForensicService:
    return ForensicService()


def get_integration_service(
    db: AsyncSession = Depends(get_db_session),
) -> IntegrationService:
    return IntegrationService(PostgresIntegrationRepository(db))


def get_investigation_service(
    db: AsyncSession = Depends(get_db_session),
) -> InvestigationService:
    return InvestigationService(PostgresInvestigationRepository(db))


def get_investigation_forensic_service(
    db: AsyncSession = Depends(get_db_session),
) -> InvestigationForensicService:
    return InvestigationForensicService(
        investigation_service=get_investigation_service(db),
        event_service=get_event_service(db),
        evidence_service=get_evidence_service(db),
        forensic_service=get_forensic_service(),
    )


def get_policy_service() -> PolicyService:
    return PolicyService()


def get_risk_service() -> RiskService:
    return RiskService()


def get_session_service(
    db: AsyncSession = Depends(get_db_session),
) -> SessionService:
    return SessionService(PostgresSessionRepository(db))


def get_telemetry_service(
    db: AsyncSession = Depends(get_db_session),
) -> TelemetryService:
    return TelemetryService(get_event_service(db))