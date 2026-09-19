from __future__ import annotations

from app.core.config import get_settings

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


def using_dynamodb() -> bool:
    return get_settings().storage_backend.lower() == "dynamodb"


def get_agent_repository():
    if using_dynamodb():
        return DynamoDBAgentRepository()
    return PostgresAgentRepository()


def get_event_repository():
    if using_dynamodb():
        return DynamoDBEventRepository()
    return PostgresEventRepository()


def get_session_repository():
    if using_dynamodb():
        return DynamoDBSessionRepository()
    return PostgresSessionRepository()


def get_investigation_repository():
    if using_dynamodb():
        return DynamoDBInvestigationRepository()
    return PostgresInvestigationRepository()


def get_alert_repository():
    if using_dynamodb():
        return DynamoDBAlertRepository()
    return PostgresAlertRepository()


def get_evidence_repository():
    if using_dynamodb():
        return DynamoDBEvidenceRepository()
    return PostgresEvidenceRepository()


def get_integration_repository():
    if using_dynamodb():
        return DynamoDBIntegrationRepository()
    return PostgresIntegrationRepository()


def get_policy_repository():
    if using_dynamodb():
        return DynamoDBPolicyRepository()
    return PostgresPolicyRepository()


def get_report_repository():
    if using_dynamodb():
        return DynamoDBReportRepository()
    return PostgresReportRepository()


def get_user_repository():
    if using_dynamodb():
        return DynamoDBUserRepository()
    return PostgresUserRepository()