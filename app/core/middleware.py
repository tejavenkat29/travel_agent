"""HTTP middleware.

`RequestContextMiddleware` assigns every request a correlation id, binds it to
the structlog context (so all logs for one request share it), measures latency,
logs a start/end line, and echoes the id back in the `X-Request-ID` response
header for end-to-end tracing.
"""

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request id + structured access logging to every request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # Bind once; every log line in this request inherits the context.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        # Make the id available to downstream handlers (e.g. error envelope).
        request.state.request_id = request_id

        start = time.perf_counter()
        logger.info("request.started")
        try:
            response = await call_next(request)
        except Exception:
            # Let the registered exception handlers build the response; just
            # record that the request failed before re-raising.
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.exception("request.failed", duration_ms=round(elapsed_ms, 2))
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "request.finished",
            status_code=response.status_code,
            duration_ms=round(elapsed_ms, 2),
        )
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


# Conservative security headers applied to every response.
_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-XSS-Protection": "0",  # modern browsers; rely on CSP instead
    "Content-Security-Policy": "default-src 'self'",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds standard hardening headers to every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for header, value in _SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        return response
