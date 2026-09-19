from __future__ import annotations

import asyncio
from typing import Any

from app.infrastructure.aws.dynamodb import get_dynamodb_table
from app.repositories.interfaces import ReportRepository, RepositoryListResult


class DynamoDBReportRepository(ReportRepository):
    def __init__(self) -> None:
        self.table = get_dynamodb_table()

    @staticmethod
    def _key(report_id: str) -> dict[str, str]:
        return {
            "PK": f"REPORT#{report_id}",
            "SK": "METADATA",
        }

    @staticmethod
    def _to_dict(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "report_id": item["report_id"],
            "investigation_id": item.get("investigation_id"),
            "report_type": item.get("report_type"),
            "status": item.get("status"),
            "title": item.get("title"),
            "content": item.get("content"),
            "storage_uri": item.get("storage_uri"),
            "metadata": item.get("metadata", {}),
        }

    def _build_item(self, report: Any) -> dict[str, Any]:
        return {
            **self._key(report.report_id),
            "entity_type": "report",
            "entity_id": report.report_id,
            "report_id": report.report_id,
            "investigation_id": report.investigation_id,
            "report_type": report.report_type,
            "status": (
                report.status.value
                if hasattr(report.status, "value")
                else str(report.status)
            ),
            "title": report.title,
            "content": report.content,
            "storage_uri": report.storage_uri,
            "metadata": report.metadata or {},
        }

    async def get_by_id(self, report_id: str) -> Any:
        result = await self.get_optional_by_id(report_id)

        if result is None:
            raise KeyError(f"Report '{report_id}' was not found")

        return result

    async def get_optional_by_id(
        self,
        report_id: str,
    ) -> Any | None:
        response = await asyncio.to_thread(
            self.table.get_item,
            Key=self._key(report_id),
        )

        item = response.get("Item")

        if item is None:
            return None

        return self._to_dict(item)

    async def create(self, report: Any) -> Any:
        item = self._build_item(report)

        await asyncio.to_thread(
            self.table.put_item,
            Item=item,
        )

        return self._to_dict(item)

    async def create_unique(self, report: Any) -> Any:
        item = self._build_item(report)

        def operation() -> None:
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(PK)",
            )

        await asyncio.to_thread(operation)

        return self._to_dict(item)

    async def update(self, report: Any) -> Any:
        item = self._build_item(report)

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
        investigation_id: str | None = None,
        report_type: str | None = None,
        status: str | None = None,
    ) -> RepositoryListResult[Any]:
        def operation() -> list[dict[str, Any]]:
            response = self.table.scan()

            items = [
                item
                for item in response.get("Items", [])
                if item.get("entity_type") == "report"
            ]

            if investigation_id:
                items = [
                    item
                    for item in items
                    if item.get("investigation_id") == investigation_id
                ]

            if report_type:
                items = [
                    item
                    for item in items
                    if item.get("report_type") == report_type
                ]

            if status:
                items = [
                    item
                    for item in items
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