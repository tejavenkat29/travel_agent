"""Cache service factory.

Returns a single, process-wide `CacheService` chosen by configuration:
`CACHE_BACKEND=redis` (default) or `memory`. Cached via `lru_cache` so one
Redis client/connection pool is reused everywhere.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.core.logging import get_logger
from app.domain.interfaces.cache import CacheService
from app.infrastructure.cache.memory_cache import InMemoryCacheService

logger = get_logger(__name__)


@lru_cache
def get_cache_service() -> CacheService:
    """Build (once) the configured cache backend."""
    if settings.CACHE_BACKEND == "memory":
        logger.info("cache.backend_selected", backend="memory")
        return InMemoryCacheService()

    from app.infrastructure.cache.redis_cache import RedisCacheService

    logger.info("cache.backend_selected", backend="redis")
    return RedisCacheService.from_url(settings.REDIS_URL)
