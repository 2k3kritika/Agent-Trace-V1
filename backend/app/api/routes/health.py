from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

settings = get_settings()


@router.get("")
async def health_check() -> dict[str, str]:
    """
    Lightweight application health endpoint.

    This endpoint intentionally does not query the database.
    Database readiness checks can be added later through a dedicated
    infrastructure/service layer without violating the route -> service
    -> repository architecture.
    """
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }


@router.get("/live")
async def liveness_check() -> dict[str, str]:
    """
    Kubernetes/serverless-friendly liveness endpoint.

    Returns successfully as long as the FastAPI application is running.
    """
    return {
        "status": "alive",
    }