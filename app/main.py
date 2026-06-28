"""FastAPI application entrypoint.

Application factory that assembles every cross-cutting concern in one place:
configuration, structured logging, request-context middleware, CORS,
centralised error handling, Swagger/OpenAPI metadata, and the route tree
(un-versioned system routes + the versioned `/api/v1` router).

Run locally:
    uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.system import router as system_router
from app.api.v1.router import api_router as v1_router
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestContextMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hooks.

    Resource initialisation (DB pool, Redis client, LLM clients) will be added
    here once the infrastructure layer is implemented.
    """
    configure_logging()
    logger.info(
        "application.startup",
        env=settings.APP_ENV.value,
        version=settings.APP_VERSION,
    )
    yield
    logger.info("application.shutdown")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Production-ready backend for the AI Multi-Agent Travel Planner. "
            "Interactive docs at `/docs` (Swagger) and `/redoc`."
        ),
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # --- Middleware (outermost first) ---
    app.add_middleware(RequestContextMiddleware)
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(o) for o in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # --- Error handling ---
    register_exception_handlers(app)

    # --- Routes ---
    app.include_router(system_router)  # GET / and GET /health (un-versioned)
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
