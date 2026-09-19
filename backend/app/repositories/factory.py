from __future__ import annotations

from typing import Literal

from app.core.config import get_settings

StorageBackend = Literal["postgres", "dynamodb"]


def get_storage_backend() -> StorageBackend:
    settings = get_settings()

    backend = settings.storage_backend.lower()

    if backend not in {"postgres", "dynamodb"}:
        raise ValueError(f"Unsupported STORAGE_BACKEND: {settings.storage_backend}")

    return backend


def is_postgres_backend() -> bool:
    return get_storage_backend() == "postgres"


def is_dynamodb_backend() -> bool:
    return get_storage_backend() == "dynamodb"
