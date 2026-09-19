from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from boto3.dynamodb.conditions import Key

from app.domain.events.types import EventSeverity
from app.repositories.interfaces import EventRepository, RepositoryListResult
from app.schemas.events import CanonicalEventResponse
from app.infrastructure.aws.dynamodb import get_dynamodb_table


class DynamoDBEventRepository(EventRepository):
    """
    DynamoDB implementation of the event repository.

    Single-table key strategy:

        PK = SESSION#{session_id}
        SK = EVENT#{timestamp}#{event_id}

    Additional GSI-compatible attributes are stored for future querying.
    """

    def __init__(self) -> None:
        self.table = get_dynamodb_table()

    @staticmethod
    def _item_to_response(item: dict[str, Any]) -> CanonicalEventResponse:
        return CanonicalEventResponse(
            event_id=item["event_id"],
            timestamp=datetime.fromisoformat(item["timestamp"]),
            session_id=item.get("session_id"),
            agent_id=item["agent_id"],
            provider=item.get("provider"),
            event_type=item["event_type"],
            status=item.get("status"),
            tool=item.get("tool"),
            source=item.get("source"),
            severity=item.get("severity"),
            details=item.get("details", {}),
            metadata=item.get("metadata", {}),
            parent_event_id=item.get("parent_event_id"),
            related_event_id=item.get("related_event_id"),
            trace_id=item.get("trace_id"),
            span_id=item.get("span_id"),
        )

    @staticmethod
    def _key(
        event_id: str,
        session_id: str | None,
        timestamp: datetime | None = None,
    ) -> tuple[str, str]:
        session_key = session_id or "unknown"
        event_timestamp = timestamp or datetime.utcnow()

        return (
            f"SESSION#{session_key}",
            f"EVENT#{event_timestamp.isoformat()}#{event_id}",
        )

    def _build_item(self, event: Any) -> dict[str, Any]:
        timestamp = event.timestamp

        pk, sk = self._key(
            event_id=event.event_id,
            session_id=event.session_id,
            timestamp=timestamp,
        )

        return {
            "PK": pk,
            "SK": sk,
            "entity_type": "event",
            "entity_id": event.event_id,
            "event_id": event.event_id,
            "timestamp": timestamp.isoformat(),
            "session_id": event.session_id,
            "agent_id": event.agent_id,
            "provider": event.provider,
            "event_type": (
                event.event_type.value
                if hasattr(event.event_type, "value")
                else str(event.event_type)
            ),
            "status": (
                event.status.value
                if hasattr(event.status, "value")
                else str(event.status)
            ),
            "tool": event.tool,
            "source": event.source,
            "severity": (
                event.severity.value
                if hasattr(event.severity, "value")
                else str(event.severity)
            ),
            "details": event.details or {},
            "metadata": event.metadata or {},
            "parent_event_id": event.parent_event_id,
            "related_event_id": event.related_event_id,
            "trace_id": event.trace_id,
            "span_id": event.span_id,
        }

    async def get_by_id(self, event_id: str) -> CanonicalEventResponse:
        return await self.get_optional_by_id(event_id)

    async def get_optional_by_id(
        self,
        event_id: str,
    ) -> CanonicalEventResponse | None:
        def operation() -> dict[str, Any] | None:
            response = self.table.scan(
                FilterExpression=Key("entity_id").eq(event_id),
            )

            items = response.get("Items", [])

            if not items:
                return None

            return items[0]

        item = await asyncio.to_thread(operation)

        if item is None:
            return None

        return self._item_to_response(item)

    async def get_by_event_id(
        self,
        event_id: str,
    ) -> CanonicalEventResponse:
        result = await self.get_optional_by_id(event_id)

        if result is None:
            raise KeyError(f"Event '{event_id}' was not found")

        return result

    async def create(
        self,
        event: Any,
    ) -> CanonicalEventResponse:
        item = self._build_item(event)

        await asyncio.to_thread(
            self.table.put_item,
            Item=item,
        )

        return self._item_to_response(item)

    async def create_unique(
        self,
        event: Any,
    ) -> CanonicalEventResponse:
        item = self._build_item(event)

        def operation() -> None:
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(PK)",
            )

        try:
            await asyncio.to_thread(operation)
        except Exception as exc:
            if "ConditionalCheckFailedException" in str(exc):
                existing = await self.get_optional_by_id(event.event_id)

                if existing is not None:
                    return existing

            raise

        return self._item_to_response(item)

    async def list_page(
        self,
        page: int = 1,
        page_size: int = 25,
        *,
        agent_id: str | None = None,
        session_id: str | None = None,
        event_type: str | None = None,
        severity: EventSeverity | None = None,
    ) -> RepositoryListResult[CanonicalEventResponse]:
        def operation() -> list[dict[str, Any]]:
            if session_id:
                response = self.table.query(
                    KeyConditionExpression=Key("PK").eq(
                        f"SESSION#{session_id}"
                    ),
                )
                items = response.get("Items", [])
            else:
                response = self.table.scan()
                items = [
                    item
                    for item in response.get("Items", [])
                    if item.get("entity_type") == "event"
                ]

            if agent_id:
                items = [
                    item
                    for item in items
                    if item.get("agent_id") == agent_id
                ]

            if event_type:
                items = [
                    item
                    for item in items
                    if item.get("event_type") == event_type
                ]

            if severity:
                severity_value = (
                    severity.value
                    if hasattr(severity, "value")
                    else str(severity)
                )

                items = [
                    item
                    for item in items
                    if item.get("severity") == severity_value
                ]

            return sorted(
                items,
                key=lambda item: item.get("timestamp", ""),
                reverse=True,
            )

        items = await asyncio.to_thread(operation)

        total = len(items)
        start = max(page - 1, 0) * page_size
        end = start + page_size

        page_items = [
            self._item_to_response(item)
            for item in items[start:end]
        ]

        return RepositoryListResult(
            items=page_items,
            total=total,
        )

    async def list_session_events(
        self,
        session_id: str,
    ) -> list[CanonicalEventResponse]:
        result = await self.list_page(
            page=1,
            page_size=10000,
            session_id=session_id,
        )

        return result.items

    async def list_security_events(
        self,
        page: int = 1,
        page_size: int = 25,
    ) -> RepositoryListResult[CanonicalEventResponse]:
        security_types = {
            "UNTRUSTED_CONTENT",
            "PROMPT_INJECTION_DETECTED",
            "SENSITIVE_ACTION_ATTEMPTED",
            "POLICY_VIOLATION",
            "TOOL_BLOCKED",
            "AUDIT_LOG",
        }

        result = await self.list_page(
            page=1,
            page_size=10000,
        )

        filtered = [
            event
            for event in result.items
            if (
                event.event_type.value
                if hasattr(event.event_type, "value")
                else str(event.event_type)
            )
            in security_types
        ]

        total = len(filtered)
        start = max(page - 1, 0) * page_size
        end = start + page_size

        return RepositoryListResult(
            items=filtered[start:end],
            total=total,
        )