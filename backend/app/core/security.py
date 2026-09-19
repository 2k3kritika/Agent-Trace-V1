from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from app.core.config import get_settings
from app.core.exceptions import AppError

settings = get_settings()


_PASSWORD_ALGORITHM = "scrypt"
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SALT_BYTES = 16


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    if not password:
        raise AppError(
            status_code=400,
            message="Password cannot be empty.",
            code="INVALID_PASSWORD",
        )

    salt = secrets.token_bytes(_SALT_BYTES)

    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
    )

    return (
        f"{_PASSWORD_ALGORITHM}$"
        f"{_SCRYPT_N}$"
        f"{_SCRYPT_R}$"
        f"{_SCRYPT_P}$"
        f"{_b64encode(salt)}$"
        f"{_b64encode(derived_key)}"
    )


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        (
            algorithm,
            n,
            r,
            p,
            encoded_salt,
            encoded_key,
        ) = encoded_hash.split("$")

        if algorithm != _PASSWORD_ALGORITHM:
            return False

        salt = _b64decode(encoded_salt)
        expected_key = _b64decode(encoded_key)

        actual_key = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
        )

        return hmac.compare_digest(actual_key, expected_key)

    except (ValueError, TypeError):
        return False


def _sign(data: bytes) -> str:
    secret = settings.jwt_secret_key.encode("utf-8")

    signature = hmac.new(
        secret,
        data,
        hashlib.sha256,
    ).digest()

    return _b64encode(signature)


def create_access_token(
    user_id: str,
    email: str,
    role: str,
) -> tuple[str, int]:
    expires_in = settings.access_token_expire_minutes * 60
    now = int(time.time())

    header = {
        "alg": settings.jwt_algorithm,
        "typ": "JWT",
    }

    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + expires_in,
    }

    encoded_header = _b64encode(
        json.dumps(
            header,
            separators=(",", ":"),
        ).encode("utf-8")
    )

    encoded_payload = _b64encode(
        json.dumps(
            payload,
            separators=(",", ":"),
        ).encode("utf-8")
    )

    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = _sign(signing_input)

    return (
        f"{encoded_header}.{encoded_payload}.{signature}",
        expires_in,
    )


def create_refresh_token(
    user_id: str,
    email: str,
    role: str,
) -> tuple[str, int]:
    expires_in = settings.refresh_token_expire_days * 24 * 60 * 60
    now = int(time.time())

    header = {
        "alg": settings.jwt_algorithm,
        "typ": "JWT",
    }

    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "refresh",
        "iat": now,
        "exp": now + expires_in,
    }

    encoded_header = _b64encode(
        json.dumps(
            header,
            separators=(",", ":"),
        ).encode("utf-8")
    )

    encoded_payload = _b64encode(
        json.dumps(
            payload,
            separators=(",", ":"),
        ).encode("utf-8")
    )

    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = _sign(signing_input)

    return (
        f"{encoded_header}.{encoded_payload}.{signature}",
        expires_in,
    )


def decode_token(
    token: str,
    expected_type: str = "access",
) -> dict[str, Any]:
    try:
        parts = token.split(".")

        if len(parts) != 3:
            raise ValueError("Invalid token structure.")

        encoded_header, encoded_payload, encoded_signature = parts

        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")

        expected_signature = _sign(signing_input)

        if not hmac.compare_digest(
            encoded_signature,
            expected_signature,
        ):
            raise ValueError("Invalid token signature.")

        header = json.loads(_b64decode(encoded_header).decode("utf-8"))

        payload = json.loads(_b64decode(encoded_payload).decode("utf-8"))

        if header.get("alg") != settings.jwt_algorithm:
            raise ValueError("Unsupported token algorithm.")

        if payload.get("type") != expected_type:
            raise ValueError("Invalid token type.")

        expiration = payload.get("exp")

        if not isinstance(expiration, int):
            raise TypeError("Invalid expiration.")

        if expiration <= int(time.time()):
            raise ValueError("Token expired.")

        if not payload.get("sub"):
            raise ValueError("Token subject missing.")

        return payload

    except (ValueError, TypeError, json.JSONDecodeError):
        raise AppError(
            status_code=401,
            message="Invalid or expired authentication token.",
            code="INVALID_TOKEN",
        ) from None
