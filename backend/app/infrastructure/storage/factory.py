from __future__ import annotations

from typing import Literal

from app.core.config import get_settings
from app.infrastructure.storage.local import LocalArtifactStorage
from app.infrastructure.storage.s3 import S3ArtifactStorage

StorageProvider = Literal["local", "s3"]


def get_storage_provider() -> StorageProvider:
    settings = get_settings()

    provider = settings.storage_backend.lower()

    if provider == "dynamodb":
        return "s3"

    if provider == "postgres":
        return "local"

    raise ValueError(f"Unsupported STORAGE_BACKEND: {settings.storage_backend}")


def create_artifact_storage():
    provider = get_storage_provider()

    if provider == "s3":
        return S3ArtifactStorage()

    return LocalArtifactStorage()
