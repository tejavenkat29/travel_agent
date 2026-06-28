"""System / operational routes.

Hosts the root (`GET /`) and health (`GET /health`) endpoints. These are
intentionally *un-versioned*: liveness probes and service metadata are
operational concerns consumed by load balancers, orchestrators (Kubernetes)
and uptime monitors, so their path must stay stable across API versions.
Business endpoints live under the versioned `/api/v1` router instead.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse, HealthStatus, RootResponse

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
