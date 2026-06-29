"""Rate-limiting middleware.

Fixed-window limiter keyed by client IP, backed by the shared cache
(`CacheService.incr`). With the Redis backend this is **distributed** — the
limit holds across all API replicas, not per-process. Health/docs paths are
exempt so probes and monitoring are never throttled.

On exceeding the limit, returns 429 in the standard `ErrorResponse` envelope
and sets `X-RateLimit-*` / `Retry-After` headers.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.logging import get_logger
from app.schemas.common import ErrorResponse

logger = get_logger(__name__)

# Paths that must never be rate limited (probes, docs, schema).
_EXEMPT_PREFIXES = ("/health", "/docs", "/redoc", "/openapi.json")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP fixed-window rate limiting."""

    def __init__(self, app, *, limit: int, window: int) -> None:
        super().__init__(app)
        self._limit = limit
        self._window = window

    def _client_ip(self, request: Request) -> str:
        # Honour the first X-Forwarded-For hop when behind a proxy/LB.
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path.startswith(_EXEMPT_PREFIXES):
            return await call_next(request)

        # Imported here so the app/tests load without a cache backend wired.
        from app.infrastructure.cache.factory import get_cache_service

        ip = self._client_ip(request)
        key = f"ratelimit:{ip}"
        count = await get_cache_service().incr(key, ttl=self._window)
        remaining = max(self._limit - count, 0)

        if count > self._limit:
            logger.warning("ratelimit.exceeded", ip=ip, count=count)
            payload = ErrorResponse(
                error="rate_limited",
                message="Too many requests. Please slow down.",
                request_id=getattr(request.state, "request_id", None),
            )
            return JSONResponse(
                status_code=429,
                content=payload.model_dump(),
                headers={
                    "Retry-After": str(self._window),
                    "X-RateLimit-Limit": str(self._limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self._limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
