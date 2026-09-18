from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.infrastructure.postgres.models import Agent
from app.repositories.interfaces import (
    AgentRepository,
    RepositoryListResult,
)


class AgentService:
    """Application service for registered AI agents."""

    def __init__(
        self,
        repository: AgentRepository,
    ) -> None:
        self.repository = repository

    async def get_agent(
        self,
        agent_id: str,
    ) -> Agent:
        return await self.repository.get_by_agent_id(agent_id)

    async def get_agent_optional(
        self,
        agent_id: str,
    ) -> Agent | None:
        return await self.repository.get_optional_by_agent_id(
            agent_id
        )

    async def register_agent(
        self,
        *,
        agent_id: str,
        name: str,
        provider: str,
        description: str | None = None,
        provider_display_name: str | None = None,
        integration_type: str | None = None,
        capabilities: dict[str, Any] | None = None,
    ) -> Agent:
        existing = await self.repository.get_optional_by_agent_id(
            agent_id
        )

        if existing is not None:
            return existing

        agent = Agent(
            agent_id=agent_id,
            name=name,
            description=description,
            provider=provider,
            provider_display_name=provider_display_name,
            status="active",
            risk_score=0,
            risk_level="low",
            last_seen=datetime.now(timezone.utc),
            integration_type=integration_type,
            capabilities=capabilities or {},
        )

        return await self.repository.create(agent)

    async def update_last_seen(
        self,
        agent_id: str,
    ) -> Agent:
        agent = await self.repository.get_by_agent_id(agent_id)

        agent.last_seen = datetime.now(timezone.utc)

        return await self.repository.update(agent)

    async def update_risk(
        self,
        agent_id: str,
        *,
        risk_score: int,
        risk_level: str,
    ) -> Agent:
        normalized_score = max(
            0,
            min(100, risk_score),
        )

        return await self.repository.update_risk(
            agent_id=agent_id,
            risk_score=normalized_score,
            risk_level=risk_level,
        )

    async def list_agents(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        provider: str | None = None,
        risk_level: str | None = None,
        search: str | None = None,
    ) -> RepositoryListResult[Agent]:
        return await self.repository.list(
            page=page,
            page_size=page_size,
            status=status,
            provider=provider,
            risk_level=risk_level,
            search=search,
        )