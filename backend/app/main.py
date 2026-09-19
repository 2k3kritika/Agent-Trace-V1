from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    agents,
    alerts,
    artifacts,
    audit,
    auth,
    correlation,
    dashboard,
    detection,
    events,
    evidence,
    forensics,
    integrations,
    investigations,
    policy,
    sessions,
    telemetry,
)
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.logging import RequestLoggingMiddleware
from app.infrastructure.postgres.database import dispose_engine

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Application startup/shutdown lifecycle.

    The database engine is created by the infrastructure layer.
    On application shutdown we dispose of its connection pool cleanly.
    """
    yield
    await dispose_engine()


app = FastAPI(
    title=settings.app_name,
    description=(
        "AgentTrace backend for AI-agent telemetry, detection, "
        "risk analysis, policy enforcement, investigations, "
        "alerts, evidence, and forensic analysis."
    ),
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

app.include_router(health_router)

app.include_router(telemetry.router)
app.include_router(events.router)
app.include_router(detection.router)
app.include_router(correlation.router)

app.include_router(agents.router)
app.include_router(sessions.router)
app.include_router(integrations.router)

app.include_router(alerts.router)
app.include_router(investigations.router)
app.include_router(evidence.router)
app.include_router(policy.router)
app.include_router(forensics.router)
app.include_router(dashboard.router)

app.include_router(artifacts.router)

app.include_router(auth.router)
app.include_router(audit.router)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """
    Basic API discovery endpoint.
    """
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }
