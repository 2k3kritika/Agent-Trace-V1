from __future__ import annotations

from app.core.exceptions import AppError
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.infrastructure.postgres.models import User
from app.repositories.interfaces import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


class AuthService:
    def __init__(
        self,
        repository: UserRepository,
    ):
        self.repository = repository

    async def register(
        self,
        request: RegisterRequest,
    ) -> UserResponse:
        normalized_email = request.email.lower().strip()

        if await self.repository.email_exists(
            normalized_email
        ):
            raise AppError(
                status_code=409,
                message="A user with this email already exists.",
                code="USER_ALREADY_EXISTS",
            )

        user = User(
            email=normalized_email,
            password_hash=hash_password(request.password),
            display_name=request.display_name.strip(),
            role="analyst",
            is_active=True,
        )

        created_user = await self.repository.create(user)

        return self._to_response(created_user)

    async def login(
        self,
        request: LoginRequest,
    ) -> TokenResponse:
        normalized_email = request.email.lower().strip()

        user = await self.repository.get_by_email(
            normalized_email
        )

        if user is None:
            raise AppError(
                status_code=401,
                message="Invalid email or password.",
                code="INVALID_CREDENTIALS",
            )

        if not user.is_active:
            raise AppError(
                status_code=403,
                message="User account is inactive.",
                code="USER_INACTIVE",
            )

        if not verify_password(
            request.password,
            user.password_hash,
        ):
            raise AppError(
                status_code=401,
                message="Invalid email or password.",
                code="INVALID_CREDENTIALS",
            )

        access_token, expires_in = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            user=self._to_response(user),
        )

    async def get_user(
        self,
        user_id: str,
    ) -> UserResponse:
        user = await self.repository.get_active_by_id(
            user_id
        )

        if user is None:
            raise AppError(
                status_code=404,
                message="Active user not found.",
                code="USER_NOT_FOUND",
            )

        return self._to_response(user)

    @staticmethod
    def _to_response(
        user: User,
    ) -> UserResponse:
        return UserResponse(
            user_id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
            is_active=user.is_active,
        )