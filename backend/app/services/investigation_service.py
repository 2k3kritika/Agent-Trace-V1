from __future__ import annotations

from typing import Any

from app.infrastructure.postgres.models import Investigation
from app.repositories.interfaces import InvestigationRepository


class InvestigationService:
    """
    Application service for investigation lifecycle management.

    Investigation state is persisted through InvestigationRepository.
    Routes never access SQLAlchemy directly.
    """

    def __init__(
        self,
        repository: InvestigationRepository,
    ) -> None:
        self.repository = repository

    async def create_investigation(
        self,
        *,
        session_id: str | None = None,
        agent_id: str | None = None,
        status: str = "OPEN",
        risk_score: int = 0,
        risk_level: str = "LOW",
        scenario: str | None = None,
        verdict_type: str | None = None,
        attack_vector: str | None = None,
        impact: str | None = None,
        sensitive_action_attempted: bool = False,
        sensitive_action_executed: bool = False,
        policy_violation: bool = False,
        action_blocked: bool = False,
        external_transmission: bool = False,
        summary: dict[str, Any] | None = None,
        graph: dict[str, Any] | None = None,
    ) -> Investigation:
        investigation = Investigation(
            session_id=session_id,
            agent_id=agent_id,
            status=status,
            risk_score=risk_score,
            risk_level=risk_level,
            scenario=scenario,
            verdict_type=verdict_type,
            attack_vector=attack_vector,
            impact=impact,
            sensitive_action_attempted=sensitive_action_attempted,
            sensitive_action_executed=sensitive_action_executed,
            policy_violation=policy_violation,
            action_blocked=action_blocked,
            external_transmission=external_transmission,
            summary=summary or {},
            graph=graph or {},
        )

        return await self.repository.create(investigation)

    async def get_investigation(
        self,
        investigation_id: str,
    ) -> Investigation:
        return await self.repository.get_by_id(
            investigation_id
        )

    async def update_investigation(
        self,
        investigation_id: str,
        **updates: Any,
    ) -> Investigation:
        cleaned_updates = {
            key: value
            for key, value in updates.items()
            if value is not None
        }

        if not cleaned_updates:
            return await self.get_investigation(
                investigation_id
            )

        return await self.repository.update(
            investigation_id,
            cleaned_updates,
        )

    async def update_risk(
        self,
        investigation_id: str,
        *,
        risk_score: int,
        risk_level: str,
    ) -> Investigation:
        return await self.repository.update(
            investigation_id,
            {
                "risk_score": risk_score,
                "risk_level": risk_level,
            },
        )

    async def update_security_state(
        self,
        investigation_id: str,
        *,
        sensitive_action_attempted: bool | None = None,
        sensitive_action_executed: bool | None = None,
        policy_violation: bool | None = None,
        action_blocked: bool | None = None,
        external_transmission: bool | None = None,
    ) -> Investigation:
        updates = {
            "sensitive_action_attempted": sensitive_action_attempted,
            "sensitive_action_executed": sensitive_action_executed,
            "policy_violation": policy_violation,
            "action_blocked": action_blocked,
            "external_transmission": external_transmission,
        }

        return await self.update_investigation(
            investigation_id,
            **updates,
        )

    async def close_investigation(
        self,
        investigation_id: str,
    ) -> Investigation:
        return await self.repository.update(
            investigation_id,
            {
                "status": "CLOSED",
            },
        )

    async def list_investigations(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        agent_id: str | None = None,
        session_id: str | None = None,
        status: str | None = None,
        risk_level: str | None = None,
    ):
        filters: dict[str, Any] = {}

        if agent_id is not None:
            filters["agent_id"] = agent_id

        if session_id is not None:
            filters["session_id"] = session_id

        if status is not None:
            filters["status"] = status

        if risk_level is not None:
            filters["risk_level"] = risk_level

        return await self.repository.list_page(
            page=page,
            page_size=page_size,
            filters=filters,
        )