from __future__ import annotations

from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.infrastructure.postgres.session import get_repository_session

from app.repositories.postgres.agent import PostgresAgentRepository
from app.repositories.postgres.alert import PostgresAlertRepository
from app.repositories.postgres.event import PostgresEventRepository
from app.repositories.postgres.evidence import PostgresEvidenceRepository
from app.repositories.postgres.integration import PostgresIntegrationRepository
from app.repositories.postgres.investigation import (
    PostgresInvestigationRepository,
)
from app.repositories.postgres.policy import PostgresPolicyRepository
from app.repositories.postgres.report import PostgresReportRepository
from app.repositories.postgres.session import PostgresSessionRepository
from app.repositories.postgres.user import PostgresUserRepository


class RepositoryProvider:
    """
    Creates PostgreSQL repository instances using the request-scoped
    SQLAlchemy AsyncSession supplied by FastAPI.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.settings = get_settings()
        self.session = session

    @property
    def use_dynamodb(self) -> bool:
        return self.settings.storage_backend.lower() == "dynamodb"

    def _ensure_supported_backend(self) -> None:
        if self.use_dynamodb:
            raise RuntimeError(
                "STORAGE_BACKEND=dynamodb is not ready yet. "
                "Use STORAGE_BACKEND=postgres while running the local backend."
            )

    def agent_repository(self) -> Any:
        self._ensure_supported_backend()
        return PostgresAgentRepository(self.session)

    def event_repository(self) -> Any:
        self._ensure_supported_backend()
        return PostgresEventRepository(self.session)

    def session_repository(self) -> Any:
        self._ensure_supported_backend()
        return PostgresSessionRepository(self.session)

    def investigation_repository(self) -> Any:
        self._ensure_supported_backend()
        return PostgresInvestigationRepository(self.session)

    def alert_repository(self) -> Any:
        self._ensure_supported_backend()
        return PostgresAlertRepository(self.session)

    def evidence_repository(self) -> Any:
        self._ensure_supported_backend()
        return PostgresEvidenceRepository(self.session)

    def integration_repository(self) -> Any:
        self._ensure_supported_backend()
        return PostgresIntegrationRepository(self.session)

    def policy_repository(self) -> Any:
        self._ensure_supported_backend()
        return PostgresPolicyRepository(self.session)

    def report_repository(self) -> Any:
        self._ensure_supported_backend()
        return PostgresReportRepository(self.session)

    def user_repository(self) -> Any:
        self._ensure_supported_backend()
        return PostgresUserRepository(self.session)


def get_repository_provider(
    session: AsyncSession = Depends(get_repository_session),
) -> RepositoryProvider:
    return RepositoryProvider(session)


def get_agent_repository(
    session: AsyncSession = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).agent_repository()


def get_event_repository(
    session: AsyncSession = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).event_repository()


def get_session_repository(
    session: AsyncSession = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).session_repository()


def get_investigation_repository(
    session: AsyncSession = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).investigation_repository()


def get_alert_repository(
    session: AsyncSession = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).alert_repository()


def get_evidence_repository(
    session: AsyncSession = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).evidence_repository()


def get_integration_repository(
    session: AsyncSession = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).integration_repository()


def get_policy_repository(
    session: AsyncSession = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).policy_repository()


def get_report_repository(
    session: AsyncSession = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).report_repository()


def get_user_repository(
    session: AsyncSession = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).user_repository()