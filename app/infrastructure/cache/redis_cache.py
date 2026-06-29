"""Redis cache backend.

`CacheService` implementation over `redis.asyncio`. Uses native key expiration
(`SET ... EX ttl`) so Redis evicts stale entries for us. `decode_responses=True`
means values come back as `str`.
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.domain.interfaces.cache import CacheService

logger = get_logger(__name__)


class RedisCacheService(CacheService):
    """Distributed cache backed by Redis."""

    def __init__(self, client) -> None:
        self._client = client

    @classmethod
    def from_url(cls, url: str) -> RedisCacheService:
        # Imported lazily so the package isn't required unless Redis is used.
        from redis.asyncio import from_url

        client = from_url(url, encoding="utf-8", decode_responses=True)
        logger.info("cache.redis_connected", url=url)
        return cls(client)

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        # `ex=None` stores without expiry; a positive ttl sets it.
        await self._client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def incr(self, key: str, ttl: int | None = None) -> int:
        # INCR is atomic; set the window expiry only when the key is created.
        count = await self._client.incr(key)
        if count == 1 and ttl:
            await self._client.expire(key, ttl)
        return count
