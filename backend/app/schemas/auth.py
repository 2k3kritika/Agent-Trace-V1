from __future__ import annotations

from pydantic import EmailStr, Field

from app.schemas.common import APIModel


class LoginRequest(APIModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class RegisterRequest(APIModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    display_name: str = Field(min_length=1, max_length=120)


class UserResponse(APIModel):
    user_id: str
    email: EmailStr
    display_name: str | None = None
    role: str
    is_active: bool


class TokenResponse(APIModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(APIModel):
    refresh_token: str = Field(min_length=1)


class MeResponse(UserResponse):
    pass