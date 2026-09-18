from __future__ import annotations

from fastapi import APIRouter, Depends

from app.domain.policy.models import PolicyEvaluationContext
from app.schemas.policy import (
    PolicyDecisionResponse,
    PolicyEvaluationRequest,
)
from app.services.dependency import get_policy_service
from app.services.policy_service import PolicyService


router = APIRouter(
    prefix="/policies",
    tags=["Policies"],
)


@router.post(
    "/evaluate",
    response_model=PolicyDecisionResponse,
)
async def evaluate_policy(
    request: PolicyEvaluationRequest,
    service: PolicyService = Depends(get_policy_service),
) -> PolicyDecisionResponse:
    """
    Evaluate an action/event against the active security policy.
    """

    context = PolicyEvaluationContext(
        event_id=request.event_id,
        event_type=request.event_type,
        tool=request.tool,
        sensitive_action=request.sensitive_action,
        prompt_injection_detected=request.prompt_injection_detected,
        untrusted_content=request.untrusted_content,
        external_transmission=request.external_transmission,
        metadata=request.metadata,
    )

    decision = service.evaluate(context)

    return PolicyDecisionResponse(
        decision=decision.decision,
        policy_id=decision.policy_id,
        policy_name=decision.policy_name,
        reason=decision.reason,
        severity=decision.severity,
        matched_rules=decision.matched_rules,
        event_id=decision.event_id,
        tool=decision.tool,
        allowed=decision.allowed,
        blocked=decision.blocked,
        metadata=decision.metadata,
    )