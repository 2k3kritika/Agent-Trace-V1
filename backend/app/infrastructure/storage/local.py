from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class StoredArtifact:
    def __init__(
        self,
        artifact_id: str,
        filename: str,
        content_type: str,
        size_bytes: int,
        storage_uri: str,
        sha256: str,
        created_at: datetime,
    ):
        self.artifact_id = artifact_id
        self.filename = filename
        self.content_type = content_type
        self.size_bytes = size_bytes
        self.storage_uri = storage_uri
        self.sha256 = sha256
        self.created_at = created_at


class LocalArtifactStorage:
    """
    Local filesystem implementation of AgentTrace artifact storage.

    This is intentionally provider-neutral. Later, an S3 implementation
    can expose the same interface without changing API/service code.
    """

    def __init__(
        self,
        base_path: str = "storage/artifacts",
    ):
        self.base_path = Path(base_path)
        self.base_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    @staticmethod
    def _safe_filename(filename: str) -> str:
        """
        Prevent path traversal while preserving a useful filename.
        """
        return Path(filename).name

    async def store(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> StoredArtifact:
        artifact_id = str(uuid4())

        safe_filename = self._safe_filename(
            filename
        )

        artifact_directory = (
            self.base_path / artifact_id
        )

        artifact_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = (
            artifact_directory / safe_filename
        )

        file_path.write_bytes(content)

        sha256 = hashlib.sha256(
            content
        ).hexdigest()

        created_at = datetime.now(
            timezone.utc
        )

        return StoredArtifact(
            artifact_id=artifact_id,
            filename=safe_filename,
            content_type=content_type,
            size_bytes=len(content),
            storage_uri=file_path.as_posix(),
            sha256=sha256,
            created_at=created_at,
        )

    async def read(
        self,
        storage_uri: str,
    ) -> bytes:
        file_path = Path(storage_uri)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Artifact does not exist: {storage_uri}"
            )

        return file_path.read_bytes()

    async def delete(
        self,
        storage_uri: str,
    ) -> None:
        file_path = Path(storage_uri)

        if file_path.exists():
            file_path.unlink()

        parent = file_path.parent

        if (
            parent.exists()
            and parent.is_dir()
            and not any(parent.iterdir())
        ):
            parent.rmdir()