from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar

from app.domain.events.types import EventSeverity
from app.infrastructure.postgres.models import (
    Agent,
    Alert,
    Event,
    Evidence,
    Integration,
    Investigation,
    Policy,
    Report,
    Session,
    User,
)

T = TypeVar("T")


@dataclass(slots=True)
class RepositoryListResult(Generic[T]):
    items: list[T]
    total: int


class UserRepository(Protocol):
    async def get_by_id(
        self,
        item_id: str,
    ) -> User | None: ...

    async def get_by_email(
        self,
        email: str,
    ) -> User | None: ...

    async def get_active_by_id(
        self,
        user_id: str,
    ) -> User | None: ...

    async def email_exists(
        self,
        email: str,
    ) -> bool: ...

    async def create(
        self,
        entity: User,
    ) -> User: ...


class AgentRepository(Protocol):
    async def get_by_id(
        self,
        item_id: str,
    ) -> Agent | None: ...

    async def get_by_agent_id(
        self,
        agent_id: str,
    ) -> Agent | None: ...

    async def get_optional_by_agent_id(
        self,
        agent_id: str,
    ) -> Agent | None: ...

    async def create(
        self,
        entity: Agent,
    ) -> Agent: ...

    async def update(
        self,
        entity: Agent,
    ) -> Agent: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        provider: str | None = None,
        risk_level: str | None = None,
        search: str | None = None,
    ) -> RepositoryListResult[Agent]: ...

    async def update_risk(
        self,
        agent_id: str,
        risk_score: int,
        risk_level: str,
    ) -> Agent | None: ...


class IntegrationRepository(Protocol):
    async def get_by_id(
        self,
        item_id: str,
    ) -> Integration | None: ...

    async def get_optional_by_id(
        self,
        item_id: str,
    ) -> Integration | None: ...

    async def create(
        self,
        entity: Integration,
    ) -> Integration: ...

    async def update(
        self,
        entity: Integration,
    ) -> Integration: ...

    async def delete(
        self,
        item_id: str,
    ) -> bool: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        agent_id: str | None = None,
        status: str | None = None,
        provider: str | None = None,
    ) -> RepositoryListResult[Integration]: ...


class EventRepository(Protocol):
    async def get_by_id(
        self,
        item_id: str,
    ) -> Event | None: ...

    async def get_by_event_id(
        self,
        event_id: str,
    ) -> Event | None: ...

    async def get_optional_by_event_id(
        self,
        event_id: str,
    ) -> Event | None: ...

    async def create(
        self,
        entity: Event,
    ) -> Event: ...

    async def create_unique(
        self,
        entity: Event,
    ) -> tuple[Event, bool]: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        session_id: str | None = None,
        agent_id: str | None = None,
        event_type: str | None = None,
        severity: EventSeverity | None = None,
        search: str | None = None,
    ) -> RepositoryListResult[Event]: ...

    async def list_session_events(
        self,
        session_id: str,
        *,
        page: int,
        page_size: int,
    ) -> RepositoryListResult[Event]: ...

    async def list_security_events(
        self,
        *,
        page: int,
        page_size: int,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> RepositoryListResult[Event]: ...


class SessionRepository(Protocol):
    async def get_by_id(
        self,
        item_id: str,
    ) -> Session | None: ...

    async def get_by_session_id(
        self,
        session_id: str,
    ) -> Session | None: ...

    async def create_unique(
        self,
        entity: Session,
    ) -> tuple[Session, bool]: ...

    async def update(
        self,
        entity: Session,
    ) -> Session: ...

    async def update_metrics(
        self,
        session_id: str,
        **metrics: Any,
    ) -> Session | None: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        agent_id: str | None = None,
        status: str | None = None,
        risk_level: str | None = None,
    ) -> RepositoryListResult[Session]: ...


class InvestigationRepository(Protocol):
    async def get_by_id(
        self,
        item_id: str,
    ) -> Investigation | None: ...

    async def create(
        self,
        entity: Investigation,
    ) -> Investigation: ...

    async def update(
        self,
        entity: Investigation,
    ) -> Investigation: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        agent_id: str | None = None,
        session_id: str | None = None,
        severity: str | None = None,
        status: str | None = None,
    ) -> RepositoryListResult[Investigation]: ...


class AlertRepository(Protocol):
    async def get_by_id(
        self,
        item_id: str,
    ) -> Alert | None: ...

    async def create(
        self,
        entity: Alert,
    ) -> Alert: ...

    async def update(
        self,
        entity: Alert,
    ) -> Alert: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        severity: str | None = None,
        status: str | None = None,
        agent_id: str | None = None,
        investigation_id: str | None = None,
    ) -> RepositoryListResult[Alert]: ...


class EvidenceRepository(Protocol):
    async def get_by_id(
        self,
        item_id: str,
    ) -> Evidence | None: ...

    async def create(
        self,
        entity: Evidence,
    ) -> Evidence: ...

    async def update(
        self,
        entity: Evidence,
    ) -> Evidence: ...

    async def delete(
        self,
        item_id: str,
    ) -> bool: ...

    async def get_by_investigation(
        self,
        investigation_id: str,
    ) -> list[Evidence]: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        investigation_id: str | None = None,
        evidence_type: str | None = None,
    ) -> RepositoryListResult[Evidence]: ...


class PolicyRepository(Protocol):
    async def get_by_id(
        self,
        item_id: str,
    ) -> Policy | None: ...

    async def create(
        self,
        entity: Policy,
    ) -> Policy: ...

    async def update(
        self,
        entity: Policy,
    ) -> Policy: ...

    async def delete(
        self,
        item_id: str,
    ) -> bool: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
    ) -> RepositoryListResult[Policy]: ...


class ReportRepository(Protocol):
    async def get_by_id(
        self,
        item_id: str,
    ) -> Report | None: ...

    async def create(
        self,
        entity: Report,
    ) -> Report: ...

    async def update(
        self,
        entity: Report,
    ) -> Report: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        investigation_id: str | None = None,
        report_type: str | None = None,
        status: str | None = None,
    ) -> RepositoryListResult[Report]: ...
