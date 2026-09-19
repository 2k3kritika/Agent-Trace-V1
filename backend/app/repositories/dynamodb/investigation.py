from __future__ import annotations

import asyncio
from typing import Any

from app.infrastructure.aws.dynamodb import get_dynamodb_table
from app.repositories.interfaces import (
    InvestigationRepository,
    RepositoryListResult,
)


class DynamoDBInvestigationRepository(InvestigationRepository):
    """
    DynamoDB investigation repository.

    Key strategy:

        PK = INVESTIGATION#{investigation_id}
        SK = METADATA
    """

    def __init__(self) -> None:
        self.table = get_dynamodb_table()

    @staticmethod
    def _key(investigation_id: str) -> dict[str, str]:
        return {
            "PK": f"INVESTIGATION#{investigation_id}",
            "SK": "METADATA",
        }

    @staticmethod
    def _to_dict(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "investigation_id": item["investigation_id"],
            "session_id": item.get("session_id"),
            "agent_id": item.get("agent_id"),
            "status": item.get("status"),
            "risk_score": float(item.get("risk_score", 0)),
            "risk_level": item.get("risk_level"),
            "scenario": item.get("scenario"),
            "verdict_type": item.get("verdict_type"),
            "attack_vector": item.get("attack_vector"),
            "impact": item.get("impact"),
            "sensitive_action_attempted": bool(
                item.get("sensitive_action_attempted", False)
            ),
            "sensitive_action_executed": bool(
                item.get("sensitive_action_executed", False)
            ),
            "policy_violation": bool(item.get("policy_violation", False)),
            "action_blocked": bool(item.get("action_blocked", False)),
            "external_transmission": bool(item.get("external_transmission", False)),
            "summary": item.get("summary", {}),
            "graph": item.get("graph", {}),
        }

    def _build_item(self, investigation: Any) -> dict[str, Any]:
        return {
            **self._key(investigation.investigation_id),
            "entity_type": "investigation",
            "entity_id": investigation.investigation_id,
            "investigation_id": investigation.investigation_id,
            "session_id": investigation.session_id,
            "agent_id": investigation.agent_id,
            "status": (
                investigation.status.value
                if hasattr(investigation.status, "value")
                else str(investigation.status)
            ),
            "risk_score": investigation.risk_score or 0,
            "risk_level": (
                investigation.risk_level.value
                if hasattr(investigation.risk_level, "value")
                else investigation.risk_level
            ),
            "scenario": investigation.scenario,
            "verdict_type": investigation.verdict_type,
            "attack_vector": investigation.attack_vector,
            "impact": investigation.impact,
            "sensitive_action_attempted": bool(
                investigation.sensitive_action_attempted
            ),
            "sensitive_action_executed": bool(investigation.sensitive_action_executed),
            "policy_violation": bool(investigation.policy_violation),
            "action_blocked": bool(investigation.action_blocked),
            "external_transmission": bool(investigation.external_transmission),
            "summary": investigation.summary or {},
            "graph": investigation.graph or {},
        }

    async def get_by_id(self, investigation_id: str) -> Any:
        result = await self.get_optional_by_id(investigation_id)

        if result is None:
            raise KeyError(f"Investigation '{investigation_id}' was not found")

        return result

    async def get_optional_by_id(
        self,
        investigation_id: str,
    ) -> Any | None:
        response = await asyncio.to_thread(
            self.table.get_item,
            Key=self._key(investigation_id),
        )

        item = response.get("Item")

        if not item:
            return None

        return self._to_dict(item)

    async def create(self, investigation: Any) -> Any:
        item = self._build_item(investigation)

        await asyncio.to_thread(
            self.table.put_item,
            Item=item,
        )

        return self._to_dict(item)

    async def create_unique(self, investigation: Any) -> Any:
        item = self._build_item(investigation)

        def operation() -> None:
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(PK)",
            )

        await asyncio.to_thread(operation)

        return self._to_dict(item)

    async def update(
        self,
        investigation: Any,
    ) -> Any:
        item = self._build_item(investigation)

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
        status: str | None = None,
        risk_level: str | None = None,
    ) -> RepositoryListResult[Any]:
        def operation() -> list[dict[str, Any]]:
            response = self.table.scan()

            items = [
                item
                for item in response.get("Items", [])
                if item.get("entity_type") == "investigation"
            ]

            if agent_id:
                items = [item for item in items if item.get("agent_id") == agent_id]

            if session_id:
                items = [item for item in items if item.get("session_id") == session_id]

            if status:
                items = [item for item in items if item.get("status") == status]

            if risk_level:
                items = [item for item in items if item.get("risk_level") == risk_level]

            return items

        items = await asyncio.to_thread(operation)

        total = len(items)
        start = max(page - 1, 0) * page_size

        return RepositoryListResult(
            items=[self._to_dict(item) for item in items[start : start + page_size]],
            total=total,
        )
