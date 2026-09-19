from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token
from app.schemas.auth import (
    LoginRequest,
    MeResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService
from app.services.dependency import get_auth_service

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

bearer_scheme = HTTPBearer(
    auto_error=False,
)


@router.post(
    "/register",
    response_model=MeResponse,
    status_code=201,
)
async def register(
    request: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> MeResponse:
    return await service.register(request)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await service.login(request)


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
    request: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await service.refresh(request.refresh_token)


@router.get(
    "/me",
    response_model=MeResponse,
)
async def me(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    service: AuthService = Depends(get_auth_service),
) -> MeResponse:
    if credentials is None:
        from app.core.exceptions import AppError

        raise AppError(
            status_code=401,
            message="Authentication required.",
            code="AUTHENTICATION_REQUIRED",
        )

    payload = decode_token(
        credentials.credentials,
        expected_type="access",
    )

    return await service.get_user(str(payload["sub"]))
