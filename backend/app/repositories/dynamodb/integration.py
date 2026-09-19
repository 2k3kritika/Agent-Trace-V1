from __future__ import annotations

import asyncio
from typing import Any

from app.infrastructure.aws.dynamodb import get_dynamodb_table
from app.repositories.interfaces import (
    IntegrationRepository,
    RepositoryListResult,
)


class DynamoDBIntegrationRepository(IntegrationRepository):
    def __init__(self) -> None:
        self.table = get_dynamodb_table()

    @staticmethod
    def _key(integration_id: str) -> dict[str, str]:
        return {
            "PK": f"INTEGRATION#{integration_id}",
            "SK": "METADATA",
        }

    @staticmethod
    def _to_dict(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "integration_id": item["integration_id"],
            "agent_id": item.get("agent_id"),
            "integration_type": item.get("integration_type"),
            "provider": item.get("provider"),
            "endpoint": item.get("endpoint"),
            "api_key_reference": item.get("api_key_reference"),
            "environment": item.get("environment"),
            "status": item.get("status"),
            "configuration": item.get("configuration", {}),
        }

    def _build_item(self, integration: Any) -> dict[str, Any]:
        return {
            **self._key(integration.integration_id),
            "entity_type": "integration",
            "entity_id": integration.integration_id,
            "integration_id": integration.integration_id,
            "agent_id": integration.agent_id,
            "integration_type": integration.integration_type,
            "provider": integration.provider,
            "endpoint": integration.endpoint,
            "api_key_reference": integration.api_key_reference,
            "environment": integration.environment,
            "status": (
                integration.status.value
                if hasattr(integration.status, "value")
                else str(integration.status)
            ),
            "configuration": integration.configuration or {},
        }

    async def get_by_id(self, integration_id: str) -> Any:
        result = await self.get_optional_by_id(integration_id)

        if result is None:
            raise KeyError(f"Integration '{integration_id}' was not found")

        return result

    async def get_optional_by_id(
        self,
        integration_id: str,
    ) -> Any | None:
        response = await asyncio.to_thread(
            self.table.get_item,
            Key=self._key(integration_id),
        )

        item = response.get("Item")

        if item is None:
            return None

        return self._to_dict(item)

    async def create(self, integration: Any) -> Any:
        item = self._build_item(integration)

        await asyncio.to_thread(
            self.table.put_item,
            Item=item,
        )

        return self._to_dict(item)

    async def create_unique(self, integration: Any) -> Any:
        item = self._build_item(integration)

        def operation() -> None:
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(PK)",
            )

        await asyncio.to_thread(operation)

        return self._to_dict(item)

    async def update(self, integration: Any) -> Any:
        item = self._build_item(integration)

        await asyncio.to_thread(
            self.table.put_item,
            Item=item,
        )

        return self._to_dict(item)

    async def delete(self, integration_id: str) -> None:
        await asyncio.to_thread(
            self.table.delete_item,
            Key=self._key(integration_id),
        )

    async def list_page(
        self,
        page: int = 1,
        page_size: int = 25,
        *,
        agent_id: str | None = None,
        provider: str | None = None,
        status: str | None = None,
    ) -> RepositoryListResult[Any]:
        def operation() -> list[dict[str, Any]]:
            response = self.table.scan()

            items = [
                item
                for item in response.get("Items", [])
                if item.get("entity_type") == "integration"
            ]

            if agent_id:
                items = [item for item in items if item.get("agent_id") == agent_id]

            if provider:
                items = [item for item in items if item.get("provider") == provider]

            if status:
                items = [item for item in items if item.get("status") == status]

            return items

        items = await asyncio.to_thread(operation)

        total = len(items)
        start = max(page - 1, 0) * page_size

        return RepositoryListResult(
            items=[self._to_dict(item) for item in items[start : start + page_size]],
            total=total,
        )
