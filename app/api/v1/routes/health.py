"""Health-check endpoint.

A trivial liveness probe so the bootstrap app runs end-to-end. Real readiness
checks (DB / Redis connectivity) will be added with the infrastructure layer.
"""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
async def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV.value}
