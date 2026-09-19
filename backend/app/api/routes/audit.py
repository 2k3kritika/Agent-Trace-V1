from __future__ import annotations

from fastapi import APIRouter, Depends

from app.schemas.audit import (
    AuditLogRequest,
    AuditLogResponse,
)
from app.schemas.auth import UserResponse
from app.services.audit_service import AuditService
from app.services.auth_dependency import get_current_user
from app.services.dependency import get_audit_service

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)


@router.post(
    "/logs",
    response_model=AuditLogResponse,
    status_code=201,
)
async def create_audit_log(
    request: AuditLogRequest,
    current_user: UserResponse = Depends(get_current_user),
    service: AuditService = Depends(get_audit_service),
) -> AuditLogResponse:
    return await service.record(
        request,
        actor_user_id=current_user.user_id,
        actor_email=str(current_user.email),
        actor_role=current_user.role,
    )
