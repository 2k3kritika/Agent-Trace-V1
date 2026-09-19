from __future__ import annotations

import os

import pytest

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("AUTH_ENABLED", "false")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/agenttrace",
)
os.environ.setdefault("STORAGE_BACKEND", "postgres")


@pytest.fixture
def sample_agent_id() -> str:
    return "test-agent"


@pytest.fixture
def sample_session_id() -> str:
    return "test-session"
