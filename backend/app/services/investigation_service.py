from __future__ import annotations

from typing import Any

from app.core.constants import RiskLevel
from app.core.exceptions import InvestigationNotFoundError
from app.infrastructure.postgres.models import Investigation
from app.repositories.interfaces import InvestigationRepository
from app.schemas.common import PaginationParams
from app.schemas.investigations import (
    InvestigationCreateRequest,
    InvestigationListResponse,
    InvestigationResponse,
    InvestigationUpdateRequest,
)


class InvestigationService:
    def __init__(self, repository: InvestigationRepository):
        self.repository = repository

    @staticmethod
    def _to_response(
        investigation: Investigation,
    ) -> InvestigationResponse:
        return InvestigationResponse.model_validate(
            {
                "id": investigation.id,
                "session_id": investigation.session_id,
                "agent_id": investigation.agent_id,
                "status": investigation.status,
                "risk_score": investigation.risk_score,
                "risk_level": investigation.risk_level,
                "scenario": investigation.scenario,
                "verdict_type": investigation.verdict_type,
                "attack_vector": investigation.attack_vector,
                "impact": investigation.impact,
                "sensitive_action_attempted": (
                    investigation.sensitive_action_attempted
                ),
                "sensitive_action_executed": (investigation.sensitive_action_executed),
                "policy_violation": investigation.policy_violation,
                "action_blocked": investigation.action_blocked,
                "external_transmission": investigation.external_transmission,
                "summary": investigation.summary or {},
                "graph": investigation.graph or {},
                "created_at": investigation.created_at,
                "updated_at": investigation.updated_at,
            }
        )

    async def create_investigation(
        self,
        request: InvestigationCreateRequest,
    ) -> InvestigationResponse:
        investigation = Investigation(
            session_id=request.session_id,
            agent_id=request.agent_id,
            status=request.status,
            risk_score=request.risk_score,
            risk_level=request.risk_level.value,
            scenario=request.scenario,
            verdict_type=request.verdict_type,
            attack_vector=request.attack_vector,
            impact=request.impact,
            sensitive_action_attempted=request.sensitive_action_attempted,
            sensitive_action_executed=request.sensitive_action_executed,
            policy_violation=request.policy_violation,
            action_blocked=request.action_blocked,
            external_transmission=request.external_transmission,
            summary=request.summary,
            graph=request.graph,
        )

        created = await self.repository.create(investigation)
        return self._to_response(created)

    async def get_investigation(
        self,
        investigation_id: str,
    ) -> InvestigationResponse:
        investigation = await self.repository.get_by_id(investigation_id)

        if investigation is None:
            raise InvestigationNotFoundError(
                f"Investigation '{investigation_id}' was not found."
            )

        return self._to_response(investigation)

    async def list_investigations(
        self,
        pagination: PaginationParams,
        session_id: str | None = None,
        agent_id: str | None = None,
        status: str | None = None,
        severity: RiskLevel | None = None,
    ) -> InvestigationListResponse:
        result = await self.repository.list_page(
            page=pagination.page,
            page_size=pagination.page_size,
            session_id=session_id,
            agent_id=agent_id,
            status=status,
            risk_level=severity.value if severity else None,
        )

        items = [self._to_response(investigation) for investigation in result.items]

        return InvestigationListResponse(
            items=items,
            page=pagination.page,
            page_size=pagination.page_size,
            total=result.total,
            has_next=(pagination.page * pagination.page_size < result.total),
        )

    async def update_investigation(
        self,
        investigation_id: str,
        request: InvestigationUpdateRequest,
    ) -> InvestigationResponse:
        investigation = await self.repository.get_by_id(investigation_id)

        if investigation is None:
            raise InvestigationNotFoundError(
                f"Investigation '{investigation_id}' was not found."
            )

        updates = request.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        if "risk_level" in updates:
            risk_level = updates["risk_level"]

            if isinstance(risk_level, RiskLevel):
                updates["risk_level"] = risk_level.value

        for field_name, value in updates.items():
            setattr(investigation, field_name, value)

        updated = await self.repository.update(
            investigation_id,
            investigation,
        )

        return self._to_response(updated)

    async def close_investigation(
        self,
        investigation_id: str,
        *,
        verdict_type: str | None = None,
        impact: str | None = None,
        summary: dict[str, Any] | None = None,
    ) -> InvestigationResponse:
        investigation = await self.repository.get_by_id(investigation_id)

        if investigation is None:
            raise InvestigationNotFoundError(
                f"Investigation '{investigation_id}' was not found."
            )

        investigation.status = "CLOSED"

        if verdict_type is not None:
            investigation.verdict_type = verdict_type

        if impact is not None:
            investigation.impact = impact

        if summary is not None:
            investigation.summary = summary

        updated = await self.repository.update(
            investigation_id,
            investigation,
        )

        return self._to_response(updated)
