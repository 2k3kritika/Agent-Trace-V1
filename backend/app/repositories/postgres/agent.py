"""PostgreSQL repository for agents."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from app.infrastructure.postgres.models import Agent
from app.repositories.interfaces import AgentRepository
from app.repositories.postgres.base import PostgresRepository


class PostgresAgentRepository(
    PostgresRepository[Agent],
    AgentRepository,
):
    """PostgreSQL implementation of AgentRepository."""

    model = Agent

    async def get_by_agent_id(self, agent_id: str) -> Agent:
        """Retrieve an agent using its external AgentTrace ID."""
        result = await self.session.execute(
            select(Agent).where(Agent.agent_id == agent_id)
        )

        agent = result.scalar_one_or_none()

        if agent is None:
            from app.core.exceptions import NotFoundError

            raise NotFoundError(
                f"Agent with agent_id '{agent_id}' was not found."
            )

        return agent

    async def get_optional_by_agent_id(
        self,
        agent_id: str,
    ) -> Agent | None:
        """Retrieve an agent or return None."""
        result = await self.session.execute(
            select(Agent).where(Agent.agent_id == agent_id)
        )

        return result.scalar_one_or_none()

    async def list_agents(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        provider: str | None = None,
        risk_level: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Agent], int]:
        """List agents with optional filtering."""
        statement = select(Agent)

        if status:
            statement = statement.where(Agent.status == status)

        if provider:
            statement = statement.where(Agent.provider == provider)

        if risk_level:
            statement = statement.where(Agent.risk_level == risk_level)

        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(
                Agent.name.ilike(pattern)
                | Agent.agent_id.ilike(pattern)
                | Agent.provider.ilike(pattern)
            )

        statement = statement.order_by(
            Agent.risk_score.desc(),
            Agent.last_seen.desc().nullslast(),
        )

        return await self.list_page(
            page=page,
            page_size=page_size,
            statement=statement,
        )

    async def update_risk(
        self,
        agent_id: str,
        *,
        risk_score: int,
        risk_level: str,
    ) -> Agent:
        """Update the current risk state of an agent."""
        agent = await self.get_by_agent_id(agent_id)

        values: dict[str, Any] = {
            "risk_score": risk_score,
            "risk_level": risk_level,
        }

        return await self.update(agent.id, values)