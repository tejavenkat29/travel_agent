"""Centralised exception handlers.

`register_exception_handlers(app)` attaches handlers that convert every failure
into the uniform `ErrorResponse` envelope, so clients always receive a
consistent error shape regardless of where the error originated:

- `AppException`            -> our domain errors (mapped status + code)
- `RequestValidationError`  -> 422 with field-level details
- `StarletteHTTPException`  -> framework HTTP errors (404 routes, etc.)
- `Exception`               -> last-resort 500 (details hidden in prod)
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.schemas.common import ErrorDetail, ErrorResponse

logger = get_logger(__name__)


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _json(status_code: int, payload: ErrorResponse) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    """Wire all exception handlers onto the FastAPI app."""

    @app.exception_handler(AppException)
    async def handle_app_exception(
        request: Request, exc: AppException
    ) -> JSONResponse:
        logger.warning("app.error", code=exc.code, message=exc.message)
        return _json(
            exc.status_code,
            ErrorResponse(
                error=exc.code,
                message=exc.message,
                request_id=_request_id(request),
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            ErrorDetail(
                field=".".join(str(p) for p in err["loc"]),
                message=err["msg"],
            )
            for err in exc.errors()
        ]
        return _json(
            422,
            ErrorResponse(
                error="validation_error",
                message="Request validation failed.",
                details=details,
                request_id=_request_id(request),
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return _json(
            exc.status_code,
            ErrorResponse(
                error="http_error",
                message=str(exc.detail),
                request_id=_request_id(request),
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("unhandled.error")
        # Never leak internals in production.
        message = str(exc) if settings.DEBUG else "An unexpected error occurred."
        return _json(
            500,
            ErrorResponse(
                error="internal_error",
                message=message,
                request_id=_request_id(request),
            ),
        )
