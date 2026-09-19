from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from app.infrastructure.aws.dynamodb import get_dynamodb_table
from app.repositories.interfaces import RepositoryListResult, SessionRepository


class DynamoDBSessionRepository(SessionRepository):
    """
    DynamoDB session repository.

    Key strategy:

        PK = SESSION#{session_id}
        SK = METADATA

    A secondary lookup item is also stored by agent.
    """

    def __init__(self) -> None:
        self.table = get_dynamodb_table()

    @staticmethod
    def _item_to_dict(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": item["session_id"],
            "agent_id": item["agent_id"],
            "provider": item.get("provider"),
            "status": item.get("status"),
            "started_at": datetime.fromisoformat(item["started_at"]),
            "ended_at": (
                datetime.fromisoformat(item["ended_at"])
                if item.get("ended_at")
                else None
            ),
            "duration": item.get("duration"),
            "event_count": int(item.get("event_count", 0)),
            "alert_count": int(item.get("alert_count", 0)),
            "risk_score": float(item.get("risk_score", 0)),
            "risk_level": item.get("risk_level"),
            "scenario": item.get("scenario"),
            "investigation_id": item.get("investigation_id"),
            "metadata": item.get("metadata", {}),
        }

    @staticmethod
    def _key(session_id: str) -> dict[str, str]:
        return {
            "PK": f"SESSION#{session_id}",
            "SK": "METADATA",
        }

    def _build_item(self, session: Any) -> dict[str, Any]:
        return {
            **self._key(session.session_id),
            "entity_type": "session",
            "entity_id": session.session_id,
            "session_id": session.session_id,
            "agent_id": session.agent_id,
            "provider": session.provider,
            "status": (
                session.status.value
                if hasattr(session.status, "value")
                else str(session.status)
            ),
            "started_at": session.started_at.isoformat(),
            "ended_at": (session.ended_at.isoformat() if session.ended_at else None),
            "duration": session.duration,
            "event_count": session.event_count or 0,
            "alert_count": session.alert_count or 0,
            "risk_score": session.risk_score or 0,
            "risk_level": (
                session.risk_level.value
                if hasattr(session.risk_level, "value")
                else session.risk_level
            ),
            "scenario": session.scenario,
            "investigation_id": session.investigation_id,
            "metadata": session.metadata or {},
        }

    async def get_by_id(self, session_id: str) -> Any:
        result = await self.get_optional_by_id(session_id)

        if result is None:
            raise KeyError(f"Session '{session_id}' was not found")

        return result

    async def get_optional_by_id(self, session_id: str) -> Any | None:
        response = await asyncio.to_thread(
            self.table.get_item,
            Key=self._key(session_id),
        )

        item = response.get("Item")

        if not item:
            return None

        return self._item_to_dict(item)

    async def get_by_session_id(self, session_id: str) -> Any:
        return await self.get_by_id(session_id)

    async def create_unique(self, session: Any) -> Any:
        item = self._build_item(session)

        def operation() -> None:
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(PK)",
            )

        await asyncio.to_thread(operation)

        return self._item_to_dict(item)

    async def create(self, session: Any) -> Any:
        item = self._build_item(session)

        await asyncio.to_thread(
            self.table.put_item,
            Item=item,
        )

        return self._item_to_dict(item)

    async def update_metrics(
        self,
        session_id: str,
        *,
        event_count: int | None = None,
        alert_count: int | None = None,
        risk_score: float | None = None,
        risk_level: str | None = None,
    ) -> Any:
        updates: dict[str, Any] = {}

        if event_count is not None:
            updates["event_count"] = event_count

        if alert_count is not None:
            updates["alert_count"] = alert_count

        if risk_score is not None:
            updates["risk_score"] = risk_score

        if risk_level is not None:
            updates["risk_level"] = risk_level

        if not updates:
            return await self.get_by_id(session_id)

        expression_parts: list[str] = []
        names: dict[str, str] = {}
        values: dict[str, Any] = {}

        for index, (field, value) in enumerate(updates.items()):
            name = f"#f{index}"
            value_name = f":v{index}"

            expression_parts.append(f"{name} = {value_name}")
            names[name] = field
            values[value_name] = value

        response = await asyncio.to_thread(
            self.table.update_item,
            Key=self._key(session_id),
            UpdateExpression="SET " + ", ".join(expression_parts),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            ReturnValues="ALL_NEW",
        )

        return self._item_to_dict(response["Attributes"])

    async def list_page(
        self,
        page: int = 1,
        page_size: int = 25,
        *,
        agent_id: str | None = None,
        status: str | None = None,
        risk_level: str | None = None,
    ) -> RepositoryListResult[Any]:
        def operation() -> list[dict[str, Any]]:
            response = self.table.scan()

            items = [
                item
                for item in response.get("Items", [])
                if item.get("entity_type") == "session"
            ]

            if agent_id:
                items = [item for item in items if item.get("agent_id") == agent_id]

            if status:
                items = [item for item in items if item.get("status") == status]

            if risk_level:
                items = [item for item in items if item.get("risk_level") == risk_level]

            return sorted(
                items,
                key=lambda item: item.get("started_at", ""),
                reverse=True,
            )

        items = await asyncio.to_thread(operation)

        total = len(items)
        start = max(page - 1, 0) * page_size

        return RepositoryListResult(
            items=[
                self._item_to_dict(item) for item in items[start : start + page_size]
            ],
            total=total,
        )
