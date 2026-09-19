from __future__ import annotations

import asyncio
from typing import Any

from app.infrastructure.aws.dynamodb import get_dynamodb_table
from app.repositories.interfaces import PolicyRepository, RepositoryListResult


class DynamoDBPolicyRepository(PolicyRepository):
    def __init__(self) -> None:
        self.table = get_dynamodb_table()

    @staticmethod
    def _key(policy_id: str) -> dict[str, str]:
        return {
            "PK": f"POLICY#{policy_id}",
            "SK": "METADATA",
        }

    @staticmethod
    def _to_dict(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "policy_id": item["policy_id"],
            "name": item.get("name"),
            "description": item.get("description"),
            "status": item.get("status"),
            "action": item.get("action"),
            "priority": int(item.get("priority", 0)),
            "rules": item.get("rules", {}),
            "metadata": item.get("metadata", {}),
        }

    def _build_item(self, policy: Any) -> dict[str, Any]:
        return {
            **self._key(policy.policy_id),
            "entity_type": "policy",
            "entity_id": policy.policy_id,
            "policy_id": policy.policy_id,
            "name": policy.name,
            "description": policy.description,
            "status": (
                policy.status.value
                if hasattr(policy.status, "value")
                else str(policy.status)
            ),
            "action": (
                policy.action.value
                if hasattr(policy.action, "value")
                else str(policy.action)
            ),
            "priority": policy.priority,
            "rules": policy.rules or {},
            "metadata": policy.metadata or {},
        }

    async def get_by_id(self, policy_id: str) -> Any:
        result = await self.get_optional_by_id(policy_id)

        if result is None:
            raise KeyError(f"Policy '{policy_id}' was not found")

        return result

    async def get_optional_by_id(
        self,
        policy_id: str,
    ) -> Any | None:
        response = await asyncio.to_thread(
            self.table.get_item,
            Key=self._key(policy_id),
        )

        item = response.get("Item")

        if item is None:
            return None

        return self._to_dict(item)

    async def create(self, policy: Any) -> Any:
        item = self._build_item(policy)

        await asyncio.to_thread(
            self.table.put_item,
            Item=item,
        )

        return self._to_dict(item)

    async def create_unique(self, policy: Any) -> Any:
        item = self._build_item(policy)

        def operation() -> None:
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(PK)",
            )

        await asyncio.to_thread(operation)

        return self._to_dict(item)

    async def update(self, policy: Any) -> Any:
        item = self._build_item(policy)

        await asyncio.to_thread(
            self.table.put_item,
            Item=item,
        )

        return self._to_dict(item)

    async def list_page(
        self,
        page: int = 1,
        page_size: int = 25,
        *,
        status: str | None = None,
    ) -> RepositoryListResult[Any]:
        def operation() -> list[dict[str, Any]]:
            response = self.table.scan()

            items = [
                item
                for item in response.get("Items", [])
                if item.get("entity_type") == "policy"
            ]

            if status:
                items = [
                    item
                    for item in items
                    if item.get("status") == status
                ]

            return sorted(
                items,
                key=lambda item: int(item.get("priority", 0)),
            )

        items = await asyncio.to_thread(operation)

        total = len(items)
        start = max(page - 1, 0) * page_size

        return RepositoryListResult(
            items=[
                self._to_dict(item)
                for item in items[start:start + page_size]
            ],
            total=total,
        )