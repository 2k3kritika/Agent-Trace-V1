from __future__ import annotations

import asyncio
from typing import Any

from app.infrastructure.aws.dynamodb import get_dynamodb_table
from app.repositories.interfaces import AlertRepository, RepositoryListResult


class DynamoDBAlertRepository(AlertRepository):
    """
    DynamoDB alert repository.

    Key strategy:

        PK = ALERT#{alert_id}
        SK = METADATA
    """

    def __init__(self) -> None:
        self.table = get_dynamodb_table()

    @staticmethod
    def _key(alert_id: str) -> dict[str, str]:
        return {
            "PK": f"ALERT#{alert_id}",
            "SK": "METADATA",
        }

    @staticmethod
    def _to_dict(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "alert_id": item["alert_id"],
            "agent_id": item.get("agent_id"),
            "session_id": item.get("session_id"),
            "investigation_id": item.get("investigation_id"),
            "title": item.get("title"),
            "description": item.get("description"),
            "severity": item.get("severity"),
            "status": item.get("status"),
            "detector_id": item.get("detector_id"),
            "metadata": item.get("metadata", {}),
        }

    def _build_item(self, alert: Any) -> dict[str, Any]:
        return {
            **self._key(alert.alert_id),
            "entity_type": "alert",
            "entity_id": alert.alert_id,
            "alert_id": alert.alert_id,
            "agent_id": alert.agent_id,
            "session_id": alert.session_id,
            "investigation_id": alert.investigation_id,
            "title": alert.title,
            "description": alert.description,
            "severity": (
                alert.severity.value
                if hasattr(alert.severity, "value")
                else str(alert.severity)
            ),
            "status": (
                alert.status.value
                if hasattr(alert.status, "value")
                else str(alert.status)
            ),
            "detector_id": alert.detector_id,
            "metadata": alert.metadata or {},
        }

    async def get_by_id(self, alert_id: str) -> Any:
        result = await self.get_optional_by_id(alert_id)

        if result is None:
            raise KeyError(f"Alert '{alert_id}' was not found")

        return result

    async def get_optional_by_id(
        self,
        alert_id: str,
    ) -> Any | None:
        response = await asyncio.to_thread(
            self.table.get_item,
            Key=self._key(alert_id),
        )

        item = response.get("Item")

        if not item:
            return None

        return self._to_dict(item)

    async def create(self, alert: Any) -> Any:
        item = self._build_item(alert)

        await asyncio.to_thread(
            self.table.put_item,
            Item=item,
        )

        return self._to_dict(item)

    async def create_unique(self, alert: Any) -> Any:
        item = self._build_item(alert)

        def operation() -> None:
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(PK)",
            )

        await asyncio.to_thread(operation)

        return self._to_dict(item)

    async def update(self, alert: Any) -> Any:
        item = self._build_item(alert)

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
        agent_id: str | None = None,
        session_id: str | None = None,
        investigation_id: str | None = None,
        severity: str | None = None,
        status: str | None = None,
    ) -> RepositoryListResult[Any]:
        def operation() -> list[dict[str, Any]]:
            response = self.table.scan()

            items = [
                item
                for item in response.get("Items", [])
                if item.get("entity_type") == "alert"
            ]

            if agent_id:
                items = [
                    item for item in items
                    if item.get("agent_id") == agent_id
                ]

            if session_id:
                items = [
                    item for item in items
                    if item.get("session_id") == session_id
                ]

            if investigation_id:
                items = [
                    item for item in items
                    if item.get("investigation_id") == investigation_id
                ]

            if severity:
                items = [
                    item for item in items
                    if item.get("severity") == severity
                ]

            if status:
                items = [
                    item for item in items
                    if item.get("status") == status
                ]

            return items

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