from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass

import boto3
from app.core.config import get_settings


@dataclass(slots=True)
class S3Artifact:
    artifact_id: str
    filename: str
    content_type: str
    size: int
    storage_uri: str
    sha256: str


class S3ArtifactStorage:
    """
    AWS S3 implementation of artifact storage.

    S3 is used for potentially larger forensic artifacts while
    DynamoDB stores metadata and investigation relationships.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

        self.bucket_name = self.settings.s3_bucket

        if not self.bucket_name:
            raise RuntimeError(
                "S3_BUCKET must be configured before using S3ArtifactStorage"
            )

        self.client = boto3.client(
            "s3",
            region_name=self.settings.aws_region,
            endpoint_url=self.settings.aws_endpoint_url,
        )

    @staticmethod
    def _sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _object_key(
        artifact_id: str,
        filename: str,
    ) -> str:
        safe_filename = filename.replace("/", "_").replace("\\", "_")

        return f"artifacts/{artifact_id}/{safe_filename}"

    async def save(
        self,
        *,
        artifact_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> S3Artifact:
        sha256 = self._sha256(content)

        key = self._object_key(
            artifact_id=artifact_id,
            filename=filename,
        )

        def operation() -> None:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type,
                Metadata={
                    "artifact-id": artifact_id,
                    "sha256": sha256,
                },
                ServerSideEncryption="AES256",
            )

        await asyncio.to_thread(operation)

        return S3Artifact(
            artifact_id=artifact_id,
            filename=filename,
            content_type=content_type,
            size=len(content),
            storage_uri=f"s3://{self.bucket_name}/{key}",
            sha256=sha256,
        )

    async def get(
        self,
        *,
        storage_uri: str,
    ) -> bytes:
        bucket, key = self._parse_uri(storage_uri)

        def operation() -> bytes:
            response = self.client.get_object(
                Bucket=bucket,
                Key=key,
            )

            return response["Body"].read()

        return await asyncio.to_thread(operation)

    async def delete(
        self,
        *,
        storage_uri: str,
    ) -> None:
        bucket, key = self._parse_uri(storage_uri)

        await asyncio.to_thread(
            self.client.delete_object,
            Bucket=bucket,
            Key=key,
        )

    def _parse_uri(
        self,
        storage_uri: str,
    ) -> tuple[str, str]:
        prefix = "s3://"

        if not storage_uri.startswith(prefix):
            raise ValueError("Invalid S3 storage URI. Expected s3://bucket/key")

        value = storage_uri[len(prefix) :]

        bucket, separator, key = value.partition("/")

        if not separator or not bucket or not key:
            raise ValueError("Invalid S3 storage URI. Expected s3://bucket/key")

        if bucket != self.bucket_name:
            raise ValueError("Storage URI points to an unexpected bucket")

        return bucket, key
