"""FastAPI application entrypoint.

Wires the application factory: configuration, logging, CORS and the versioned
API router. Business endpoints and agent orchestration are intentionally NOT
implemented yet — this is the bootstrap skeleton only.

Run locally:
    uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import health
from app.core.config import settings
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hooks.

    Resource initialisation (DB pool, Redis client, LLM clients) will be added
    here once the infrastructure layer is implemented.
    """
    configure_logging()
    logger.info("application.startup", env=settings.APP_ENV)
    yield
    logger.info("application.shutdown")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(o) for o in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(health.router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
