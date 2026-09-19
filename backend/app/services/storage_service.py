from __future__ import annotations

import base64
import binascii
from typing import Any


class StorageService:
    """
    Application-level wrapper around artifact storage.

    The actual implementation may be local filesystem storage or S3.
    """

    def __init__(self, storage: Any) -> None:
        self.storage = storage

    async def save_base64(
        self,
        *,
        artifact_id: str,
        filename: str,
        content_base64: str,
        content_type: str = "application/octet-stream",
    ) -> Any:
        try:
            content = base64.b64decode(
                content_base64,
                validate=True,
            )
        except (binascii.Error, ValueError) as exc:
            raise ValueError("content_base64 is not valid Base64") from exc

        return await self.storage.save(
            artifact_id=artifact_id,
            filename=filename,
            content=content,
            content_type=content_type,
        )

    async def save(
        self,
        *,
        artifact_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> Any:
        return await self.storage.save(
            artifact_id=artifact_id,
            filename=filename,
            content=content,
            content_type=content_type,
        )

    async def get(
        self,
        *,
        storage_uri: str,
    ) -> bytes:
        return await self.storage.get(
            storage_uri=storage_uri,
        )

    async def delete(
        self,
        *,
        storage_uri: str,
    ) -> None:
        await self.storage.delete(
            storage_uri=storage_uri,
        )
