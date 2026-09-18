from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar

from app.infrastructure.postgres.models import (
    Agent,
    Alert,
    Evidence,
    Event,
    Integration,
    Investigation,
    Policy,
    Report,
    Session,
)

T = TypeVar("T")


@dataclass(slots=True)
class RepositoryListResult(Generic[T]):
    items: list[T]
    total: int


class AgentRepository(Protocol):
    async def get_by_id(self, entity_id: str) -> Agent: ...
    async def get_optional_by_id(self, entity_id: str) -> Agent | None: ...
    async def get_by_agent_id(self, agent_id: str) -> Agent: ...
    async def get_optional_by_agent_id(
        self,
        agent_id: str,
    ) -> Agent | None: ...

    async def create(self, entity: Agent) -> Agent: ...
    async def update(self, entity: Agent) -> Agent: ...
    async def delete(self, entity_id: str) -> None: ...

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
    ) -> Agent: ...


class IntegrationRepository(Protocol):
    async def get_by_id(self, entity_id: str) -> Integration: ...
    async def get_optional_by_id(
        self,
        entity_id: str,
    ) -> Integration | None: ...

    async def create(self, entity: Integration) -> Integration: ...
    async def update(self, entity: Integration) -> Integration: ...
    async def delete(self, entity_id: str) -> None: ...

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
    async def get_by_id(self, entity_id: str) -> Event: ...
    async def get_optional_by_id(self, entity_id: str) -> Event | None: ...
    async def get_by_event_id(self, event_id: str) -> Event: ...
    async def get_optional_by_event_id(
        self,
        event_id: str,
    ) -> Event | None: ...

    async def create(self, entity: Event) -> Event: ...
    async def create_unique(self, entity: Event) -> Event: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        session_id: str | None = None,
        agent_id: str | None = None,
        event_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> RepositoryListResult[Event]: ...

    async def list_session_events(
        self,
        session_id: str,
    ) -> list[Event]: ...

    async def list_security_events(
        self,
        *,
        page: int,
        page_size: int,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> RepositoryListResult[Event]: ...


class SessionRepository(Protocol):
    async def get_by_id(self, entity_id: str) -> Session: ...
    async def get_optional_by_id(
        self,
        entity_id: str,
    ) -> Session | None: ...
    async def get_by_session_id(self, session_id: str) -> Session: ...
    async def get_optional_by_session_id(
        self,
        session_id: str,
    ) -> Session | None: ...

    async def create(self, entity: Session) -> Session: ...
    async def create_unique(self, entity: Session) -> Session: ...
    async def update(self, entity: Session) -> Session: ...
    async def delete(self, entity_id: str) -> None: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        agent_id: str | None = None,
        status: str | None = None,
    ) -> RepositoryListResult[Session]: ...

    async def update_metrics(
        self,
        session_id: str,
        *,
        event_count: int,
        alert_count: int,
        risk_score: int,
        risk_level: str,
    ) -> Session: ...


class InvestigationRepository(Protocol):
    async def get_by_id(
        self,
        entity_id: str,
    ) -> Investigation: ...

    async def get_optional_by_id(
        self,
        entity_id: str,
    ) -> Investigation | None: ...

    async def create(
        self,
        entity: Investigation,
    ) -> Investigation: ...

    async def update(
        self,
        entity: Investigation,
    ) -> Investigation: ...

    async def delete(
        self,
        entity_id: str,
    ) -> None: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        session_id: str | None = None,
        agent_id: str | None = None,
        status: str | None = None,
        severity: str | None = None,
    ) -> RepositoryListResult[Investigation]: ...


class AlertRepository(Protocol):
    async def get_by_id(
        self,
        entity_id: str,
    ) -> Alert: ...

    async def get_optional_by_id(
        self,
        entity_id: str,
    ) -> Alert | None: ...

    async def create(
        self,
        entity: Alert,
    ) -> Alert: ...

    async def update(
        self,
        entity: Alert,
    ) -> Alert: ...

    async def delete(
        self,
        entity_id: str,
    ) -> None: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        agent_id: str | None = None,
        session_id: str | None = None,
        investigation_id: str | None = None,
        severity: str | None = None,
        status: str | None = None,
    ) -> RepositoryListResult[Alert]: ...


class EvidenceRepository(Protocol):
    async def get_by_id(
        self,
        entity_id: str,
    ) -> Evidence: ...

    async def get_optional_by_id(
        self,
        entity_id: str,
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
        entity_id: str,
    ) -> None: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        investigation_id: str | None = None,
        evidence_type: str | None = None,
    ) -> RepositoryListResult[Evidence]: ...

    async def get_by_investigation(
        self,
        investigation_id: str,
    ) -> list[Evidence]: ...


class PolicyRepository(Protocol):
    async def get_by_id(
        self,
        entity_id: str,
    ) -> Policy: ...

    async def get_optional_by_id(
        self,
        entity_id: str,
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
        entity_id: str,
    ) -> None: ...

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
        entity_id: str,
    ) -> Report: ...

    async def get_optional_by_id(
        self,
        entity_id: str,
    ) -> Report | None: ...

    async def create(
        self,
        entity: Report,
    ) -> Report: ...

    async def update(
        self,
        entity: Report,
    ) -> Report: ...

    async def delete(
        self,
        entity_id: str,
    ) -> None: ...

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        investigation_id: str | None = None,
        report_type: str | None = None,
        status: str | None = None,
    ) -> RepositoryListResult[Report]: ...