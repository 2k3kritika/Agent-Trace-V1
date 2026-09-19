from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.security import decode_token
from app.repositories.postgres.user import PostgresUserRepository
from app.schemas.auth import UserResponse
from app.infrastructure.postgres.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession


settings = get_settings()

bearer_scheme = HTTPBearer(
    auto_error=False,
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    if not settings.auth_enabled:
        raise AppError(
            status_code=503,
            message=(
                "Authentication dependency is disabled by configuration. "
                "Set AUTH_ENABLED=true before using protected routes."
            ),
            code="AUTH_DISABLED",
        )

    if credentials is None:
        raise AppError(
            status_code=401,
            message="Authentication required.",
            code="AUTHENTICATION_REQUIRED",
        )

    payload = decode_token(
        credentials.credentials,
        expected_type="access",
    )

    user_id = str(payload["sub"])

    repository = PostgresUserRepository(db)

    user = await repository.get_active_by_id(
        user_id
    )

    if user is None:
        raise AppError(
            status_code=401,
            message="Authenticated user no longer exists or is inactive.",
            code="INVALID_USER",
        )

    return UserResponse(
        user_id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        is_active=user.is_active,
    )


def require_roles(
    *allowed_roles: str,
) -> Callable:
    async def role_dependency(
        current_user: UserResponse = Depends(
            get_current_user
        ),
    ) -> UserResponse:
        if current_user.role not in allowed_roles:
            raise AppError(
                status_code=403,
                message="You do not have permission to perform this action.",
                code="INSUFFICIENT_PERMISSIONS",
            )

        return current_user

    return role_dependency


require_admin = require_roles("admin")

require_analyst = require_roles(
    "admin",
    "analyst",
)

require_viewer = require_roles(
    "admin",
    "analyst",
    "viewer",
)