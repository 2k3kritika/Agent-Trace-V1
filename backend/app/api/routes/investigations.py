from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.schemas.investigations import (
    InvestigationCreateRequest,
    InvestigationListResponse,
    InvestigationResponse,
    InvestigationUpdateRequest,
)
from app.services.dependency import get_investigation_service
from app.services.investigation_service import InvestigationService


router = APIRouter(
    prefix="/investigations",
    tags=["Investigations"],
)


def _investigation_to_response(
    investigation,
) -> InvestigationResponse:
    return InvestigationResponse(
        investigation_id=investigation.investigation_id,
        session_id=investigation.session_id,
        agent_id=investigation.agent_id,
        status=investigation.status,
        risk_score=investigation.risk_score,
        risk_level=investigation.risk_level,
        scenario=investigation.scenario,
        verdict_type=investigation.verdict_type,
        attack_vector=investigation.attack_vector,
        impact=investigation.impact,
        sensitive_action_attempted=(
            investigation.sensitive_action_attempted
        ),
        sensitive_action_executed=(
            investigation.sensitive_action_executed
        ),
        policy_violation=investigation.policy_violation,
        action_blocked=investigation.action_blocked,
        external_transmission=(
            investigation.external_transmission
        ),
        summary=investigation.summary or {},
        graph=investigation.graph or {},
        created_at=investigation.created_at.isoformat(),
        updated_at=investigation.updated_at.isoformat(),
    )


@router.post(
    "",
    response_model=InvestigationResponse,
)
async def create_investigation(
    request: InvestigationCreateRequest,
    service: InvestigationService = Depends(
        get_investigation_service
    ),
) -> InvestigationResponse:
    investigation = await service.create_investigation(
        session_id=request.session_id,
        agent_id=request.agent_id,
        status="OPEN",
        risk_score=request.risk_score,
        risk_level=request.risk_level,
        scenario=request.scenario,
        verdict_type=request.verdict_type,
        attack_vector=request.attack_vector,
        impact=request.impact,
        sensitive_action_attempted=(
            request.sensitive_action_attempted
        ),
        sensitive_action_executed=(
            request.sensitive_action_executed
        ),
        policy_violation=request.policy_violation,
        action_blocked=request.action_blocked,
        external_transmission=(
            request.external_transmission
        ),
        summary=request.summary,
        graph=request.graph,
    )

    return _investigation_to_response(investigation)


@router.get(
    "",
    response_model=InvestigationListResponse,
)
async def list_investigations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    agent_id: str | None = None,
    session_id: str | None = None,
    status: str | None = None,
    risk_level: str | None = None,
    service: InvestigationService = Depends(
        get_investigation_service
    ),
) -> InvestigationListResponse:
    result = await service.list_investigations(
        page=page,
        page_size=page_size,
        agent_id=agent_id,
        session_id=session_id,
        status=status,
        risk_level=risk_level,
    )

    return InvestigationListResponse(
        items=[
            _investigation_to_response(item)
            for item in result.items
        ],
        page=page,
        page_size=page_size,
        total=result.total,
        has_next=(page * page_size) < result.total,
    )


@router.get(
    "/{investigation_id}",
    response_model=InvestigationResponse,
)
async def get_investigation(
    investigation_id: str,
    service: InvestigationService = Depends(
        get_investigation_service
    ),
) -> InvestigationResponse:
    investigation = await service.get_investigation(
        investigation_id
    )

    return _investigation_to_response(investigation)


@router.patch(
    "/{investigation_id}",
    response_model=InvestigationResponse,
)
async def update_investigation(
    investigation_id: str,
    request: InvestigationUpdateRequest,
    service: InvestigationService = Depends(
        get_investigation_service
    ),
) -> InvestigationResponse:
    updates = request.model_dump(
        exclude_unset=True,
    )

    investigation = await service.update_investigation(
        investigation_id,
        **updates,
    )

    return _investigation_to_response(investigation)


@router.post(
    "/{investigation_id}/close",
    response_model=InvestigationResponse,
)
async def close_investigation(
    investigation_id: str,
    service: InvestigationService = Depends(
        get_investigation_service
    ),
) -> InvestigationResponse:
    investigation = await service.close_investigation(
        investigation_id
    )

    return _investigation_to_response(investigation)