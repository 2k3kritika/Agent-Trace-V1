from __future__ import annotations

import asyncio
from typing import Any

from app.infrastructure.aws.dynamodb import get_dynamodb_table
from app.repositories.interfaces import EvidenceRepository, RepositoryListResult


class DynamoDBEvidenceRepository(EvidenceRepository):
    """
    DynamoDB evidence repository.

    Key strategy:

        PK = INVESTIGATION#{investigation_id}
        SK = EVIDENCE#{evidence_id}

    This intentionally keeps evidence physically grouped with its
    investigation, which is useful for forensic investigation retrieval.
    """

    def __init__(self) -> None:
        self.table = get_dynamodb_table()

    @staticmethod
    def _key(
        investigation_id: str,
        evidence_id: str,
    ) -> dict[str, str]:
        return {
            "PK": f"INVESTIGATION#{investigation_id}",
            "SK": f"EVIDENCE#{evidence_id}",
        }

    @staticmethod
    def _to_dict(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "evidence_id": item["evidence_id"],
            "investigation_id": item["investigation_id"],
            "event_id": item.get("event_id"),
            "evidence_type": item.get("evidence_type"),
            "title": item.get("title"),
            "description": item.get("description"),
            "storage_uri": item.get("storage_uri"),
            "sha256": item.get("sha256"),
            "content": item.get("content", {}),
            "metadata": item.get("metadata", {}),
        }

    def _build_item(self, evidence: Any) -> dict[str, Any]:
        return {
            **self._key(
                evidence.investigation_id,
                evidence.evidence_id,
            ),
            "entity_type": "evidence",
            "entity_id": evidence.evidence_id,
            "evidence_id": evidence.evidence_id,
            "investigation_id": evidence.investigation_id,
            "event_id": evidence.event_id,
            "evidence_type": evidence.evidence_type,
            "title": evidence.title,
            "description": evidence.description,
            "storage_uri": evidence.storage_uri,
            "sha256": evidence.sha256,
            "content": evidence.content or {},
            "metadata": evidence.metadata or {},
        }

    async def get_by_id(self, evidence_id: str) -> Any:
        response = await asyncio.to_thread(
            self.table.scan,
            FilterExpression=(
                "entity_type = :entity_type "
                "AND entity_id = :entity_id"
            ),
            ExpressionAttributeValues={
                ":entity_type": "evidence",
                ":entity_id": evidence_id,
            },
        )

        items = response.get("Items", [])

        if not items:
            raise KeyError(
                f"Evidence '{evidence_id}' was not found"
            )

        return self._to_dict(items[0])

    async def get_optional_by_id(
        self,
        evidence_id: str,
    ) -> Any | None:
        response = await asyncio.to_thread(
            self.table.scan,
            FilterExpression=(
                "entity_type = :entity_type "
                "AND entity_id = :entity_id"
            ),
            ExpressionAttributeValues={
                ":entity_type": "evidence",
                ":entity_id": evidence_id,
            },
        )

        items = response.get("Items", [])

        if not items:
            return None

        return self._to_dict(items[0])

    async def create(self, evidence: Any) -> Any:
        item = self._build_item(evidence)

        await asyncio.to_thread(
            self.table.put_item,
            Item=item,
        )

        return self._to_dict(item)

    async def create_unique(self, evidence: Any) -> Any:
        item = self._build_item(evidence)

        def operation() -> None:
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(PK)",
            )

        await asyncio.to_thread(operation)

        return self._to_dict(item)

    async def update(self, evidence: Any) -> Any:
        item = self._build_item(evidence)

        await asyncio.to_thread(
            self.table.put_item,
            Item=item,
        )

        return self._to_dict(item)

    async def delete(self, evidence_id: str) -> None:
        evidence = await self.get_optional_by_id(evidence_id)

        if evidence is None:
            return

        key = self._key(
            evidence["investigation_id"],
            evidence_id,
        )

        await asyncio.to_thread(
            self.table.delete_item,
            Key=key,
        )

    async def get_by_investigation(
        self,
        investigation_id: str,
    ) -> list[Any]:
        def operation() -> list[dict[str, Any]]:
            response = self.table.query(
                KeyConditionExpression=(
                    "PK = :pk AND begins_with(SK, :prefix)"
                ),
                ExpressionAttributeValues={
                    ":pk": f"INVESTIGATION#{investigation_id}",
                    ":prefix": "EVIDENCE#",
                },
            )

            return response.get("Items", [])

        items = await asyncio.to_thread(operation)

        return [
            self._to_dict(item)
            for item in items
        ]

    async def list_page(
        self,
        page: int = 1,
        page_size: int = 25,
        *,
        investigation_id: str | None = None,
        evidence_type: str | None = None,
    ) -> RepositoryListResult[Any]:
        if investigation_id:
            items = await self.get_by_investigation(
                investigation_id
            )
        else:
            def operation() -> list[dict[str, Any]]:
                response = self.table.scan()

                return [
                    item
                    for item in response.get("Items", [])
                    if item.get("entity_type") == "evidence"
                ]

            raw_items = await asyncio.to_thread(operation)

            items = [
                self._to_dict(item)
                for item in raw_items
            ]

        if evidence_type:
            items = [
                item
                for item in items
                if item.get("evidence_type") == evidence_type
            ]

        total = len(items)
        start = max(page - 1, 0) * page_size

        return RepositoryListResult(
            items=items[start:start + page_size],
            total=total,
        )