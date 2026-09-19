from __future__ import annotations

from typing import Any

from app.infrastructure.aws.dynamodb import get_dynamodb_table
from app.repositories.dynamodb.base import DynamoDBRepository
from app.repositories.interfaces import RepositoryListResult


class DynamoDBAgentRepository(DynamoDBRepository[Any]):
    entity_type = "agent"

    def __init__(self, table: Any | None = None) -> None:
        super().__init__(table or get_dynamodb_table())

    def _to_item(self, entity: Any) -> dict[str, Any]:
        return {
            "PK": f"AGENT#{entity.agent_id}",
            "SK": "METADATA",
            "entity_type": "agent",
            "entity_id": entity.agent_id,
            "agent_id": entity.agent_id,
            "name": entity.name,
            "description": entity.description,
            "provider": entity.provider,
            "provider_display_name": entity.provider_display_name,
            "status": entity.status,
            "risk_score": entity.risk_score,
            "risk_level": entity.risk_level,
            "last_seen": (
                entity.last_seen.isoformat()
                if entity.last_seen is not None
                else None
            ),
            "integration_type": entity.integration_type,
            "capabilities": entity.capabilities or {},
            "created_at": (
                entity.created_at.isoformat()
                if entity.created_at is not None
                else None
            ),
            "updated_at": (
                entity.updated_at.isoformat()
                if entity.updated_at is not None
                else None
            ),
        }

    def _from_item(self, item: dict[str, Any]) -> Any:
        from app.infrastructure.postgres.models import Agent

        return Agent(
            id=item.get("id"),
            agent_id=item["agent_id"],
            name=item.get("name", item["agent_id"]),
            description=item.get("description"),
            provider=item.get("provider", "unknown"),
            provider_display_name=item.get("provider_display_name"),
            status=item.get("status", "unknown"),
            risk_score=item.get("risk_score", 0),
            risk_level=item.get("risk_level", "LOW"),
            integration_type=item.get("integration_type"),
            capabilities=item.get("capabilities", {}),
        )

    async def get_by_id(
        self,
        entity_id: str,
    ) -> Any:
        item = self.get_by_id_sync(entity_id)

        if item is None:
            raise KeyError(f"Agent '{entity_id}' was not found.")

        return self._from_item(item)

    async def get_optional_by_id(
        self,
        entity_id: str,
    ) -> Any | None:
        item = self.get_by_id_sync(entity_id)

        if item is None:
            return None

        return self._from_item(item)

    async def get_by_agent_id(
        self,
        agent_id: str,
    ) -> Any:
        return await self.get_by_id(agent_id)

    async def get_optional_by_agent_id(
        self,
        agent_id: str,
    ) -> Any | None:
        return await self.get_optional_by_id(agent_id)

    async def create(
        self,
        entity: Any,
    ) -> Any:
        self.put_item_sync(self._to_item(entity))
        return entity

    async def create_unique(
        self,
        entity: Any,
    ) -> Any:
        item = self._to_item(entity)

        try:
            self.put_item_if_absent_sync(item)
        except Exception as exc:
            raise ValueError(
                f"Agent '{entity.agent_id}' already exists."
            ) from exc

        return entity

    async def update(
        self,
        entity: Any,
    ) -> Any:
        self.put_item_sync(self._to_item(entity))
        return entity

    async def delete(
        self,
        entity_id: str,
    ) -> bool:
        return self.delete_by_id_sync(entity_id)

    async def list_page(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        provider: str | None = None,
        risk_level: str | None = None,
        search: str | None = None,
    ) -> RepositoryListResult[Any]:
        items = self.query_partition_sync(
            "AGENTS",
            begins_with="AGENT#",
        )

        filtered: list[dict[str, Any]] = []

        for item in items:
            if status and item.get("status") != status:
                continue

            if provider and item.get("provider") != provider:
                continue

            if risk_level and item.get("risk_level") != risk_level:
                continue

            if search:
                search_value = search.lower()
                searchable = " ".join(
                    [
                        str(item.get("agent_id", "")),
                        str(item.get("name", "")),
                        str(item.get("provider", "")),
                        str(item.get("description", "")),
                    ]
                ).lower()

                if search_value not in searchable:
                    continue

            filtered.append(item)

        total = len(filtered)

        start = max((page - 1) * page_size, 0)
        end = start + page_size

        paged = filtered[start:end]

        return RepositoryListResult(
            items=[self._from_item(item) for item in paged],
            total=total,
        )

    async def update_risk(
        self,
        agent_id: str,
        risk_score: int,
        risk_level: str,
    ) -> Any:
        item = self.get_by_id_sync(agent_id)

        if item is None:
            raise KeyError(f"Agent '{agent_id}' was not found.")

        item["risk_score"] = risk_score
        item["risk_level"] = risk_level

        self.put_item_sync(item)

        return self._from_item(item)