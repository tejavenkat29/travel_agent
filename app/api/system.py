"""System / operational routes.

Hosts the root (`GET /`) and health (`GET /health`) endpoints. These are
intentionally *un-versioned*: liveness probes and service metadata are
operational concerns consumed by load balancers, orchestrators (Kubernetes)
and uptime monitors, so their path must stay stable across API versions.
Business endpoints live under the versioned `/api/v1` router instead.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.common import HealthResponse, HealthStatus, RootResponse

logger = get_logger(__name__)

router = APIRouter(tags=["system"])


@router.get(
    "/",
    response_model=RootResponse,
    summary="Service metadata",
    description="Returns basic information about the running service.",
)
async def root() -> RootResponse:
    return RootResponse(
        name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV.value,
        docs_url="/docs",
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Lightweight check used by orchestrators to verify the service "
    "is up. Readiness checks for DB/Redis are added with the infra layer.",
)
async def health() -> HealthResponse:
    return HealthResponse(
        status=HealthStatus.OK,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV.value,
    )


@router.get(
    "/health/ready",
    summary="Readiness probe",
    description="Verifies dependencies (PostgreSQL, Redis) are reachable. "
    "Returns 503 if any dependency is down so orchestrators stop routing "
    "traffic until it recovers.",
)
async def readiness() -> JSONResponse:
    checks: dict[str, str] = {}
    ok = True

    # PostgreSQL
    try:
        from sqlalchemy import text

        from app.infrastructure.db.session import get_engine

        async with get_engine().connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001 — report, don't crash
        ok = False
        checks["database"] = f"error: {type(exc).__name__}"

    # Redis / cache (round-trip)
    try:
        from app.infrastructure.cache.factory import get_cache_service

        cache = get_cache_service()
        await cache.set("health:ready", "1", ttl=5)
        await cache.get("health:ready")
        checks["cache"] = "ok"
    except Exception as exc:  # noqa: BLE001
        ok = False
        checks["cache"] = f"error: {type(exc).__name__}"

    status_code = 200 if ok else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if ok else "not_ready", "checks": checks},
    )
