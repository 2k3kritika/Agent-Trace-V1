from __future__ import annotations

from typing import Any

from app.infrastructure.postgres.session import get_repository_session
from app.repositories.dynamodb.agents import DynamoDBAgentRepository
from app.repositories.dynamodb.alert import DynamoDBAlertRepository
from app.repositories.dynamodb.event import DynamoDBEventRepository
from app.repositories.dynamodb.evidence import DynamoDBEvidenceRepository
from app.repositories.dynamodb.integration import DynamoDBIntegrationRepository
from app.repositories.dynamodb.investigation import DynamoDBInvestigationRepository
from app.repositories.dynamodb.policy import DynamoDBPolicyRepository
from app.repositories.dynamodb.report import DynamoDBReportRepository
from app.repositories.dynamodb.session import DynamoDBSessionRepository
from app.repositories.dynamodb.user import DynamoDBUserRepository
from app.repositories.factory import is_dynamodb_backend
from app.repositories.postgres.agent import PostgresAgentRepository
from app.repositories.postgres.alert import PostgresAlertRepository
from app.repositories.postgres.event import PostgresEventRepository
from app.repositories.postgres.evidence import PostgresEvidenceRepository
from app.repositories.postgres.integration import PostgresIntegrationRepository
from app.repositories.postgres.investigation import PostgresInvestigationRepository
from app.repositories.postgres.policy import PostgresPolicyRepository
from app.repositories.postgres.report import PostgresReportRepository
from app.repositories.postgres.session import PostgresSessionRepository
from app.repositories.postgres.user import PostgresUserRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class RepositoryProvider:
    """
    Provides repositories for the configured storage backend.

    Local/test environments use PostgreSQL.
    AWS uses DynamoDB.
    """

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session

    @property
    def use_dynamodb(self) -> bool:
        return is_dynamodb_backend()

    def _require_postgres_session(self) -> AsyncSession:
        if self.session is None:
            raise RuntimeError(
                "PostgreSQL repository requested without an AsyncSession."
            )
        return self.session

    def agent_repository(self) -> Any:
        if self.use_dynamodb:
            return DynamoDBAgentRepository()

        return PostgresAgentRepository(self._require_postgres_session())

    def alert_repository(self) -> Any:
        if self.use_dynamodb:
            return DynamoDBAlertRepository()

        return PostgresAlertRepository(self._require_postgres_session())

    def event_repository(self) -> Any:
        if self.use_dynamodb:
            return DynamoDBEventRepository()

        return PostgresEventRepository(self._require_postgres_session())

    def evidence_repository(self) -> Any:
        if self.use_dynamodb:
            return DynamoDBEvidenceRepository()

        return PostgresEvidenceRepository(self._require_postgres_session())

    def integration_repository(self) -> Any:
        if self.use_dynamodb:
            return DynamoDBIntegrationRepository()

        return PostgresIntegrationRepository(self._require_postgres_session())

    def investigation_repository(self) -> Any:
        if self.use_dynamodb:
            return DynamoDBInvestigationRepository()

        return PostgresInvestigationRepository(self._require_postgres_session())

    def policy_repository(self) -> Any:
        if self.use_dynamodb:
            return DynamoDBPolicyRepository()

        return PostgresPolicyRepository(self._require_postgres_session())

    def report_repository(self) -> Any:
        if self.use_dynamodb:
            return DynamoDBReportRepository()

        return PostgresReportRepository(self._require_postgres_session())

    def session_repository(self) -> Any:
        if self.use_dynamodb:
            return DynamoDBSessionRepository()

        return PostgresSessionRepository(self._require_postgres_session())

    def user_repository(self) -> Any:
        if self.use_dynamodb:
            return DynamoDBUserRepository()

        return PostgresUserRepository(self._require_postgres_session())


def get_repository_provider(
    session: AsyncSession | None = Depends(get_repository_session),
) -> RepositoryProvider:
    return RepositoryProvider(session)


def get_agent_repository(
    session: AsyncSession | None = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).agent_repository()


def get_alert_repository(
    session: AsyncSession | None = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).alert_repository()


def get_event_repository(
    session: AsyncSession | None = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).event_repository()


def get_evidence_repository(
    session: AsyncSession | None = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).evidence_repository()


def get_integration_repository(
    session: AsyncSession | None = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).integration_repository()


def get_investigation_repository(
    session: AsyncSession | None = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).investigation_repository()


def get_policy_repository(
    session: AsyncSession | None = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).policy_repository()


def get_report_repository(
    session: AsyncSession | None = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).report_repository()


def get_session_repository(
    session: AsyncSession | None = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).session_repository()


def get_user_repository(
    session: AsyncSession | None = Depends(get_repository_session),
) -> Any:
    return RepositoryProvider(session).user_repository()