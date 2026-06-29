"""Caching decorator for `HotelProvider` (cache-aside)."""

from __future__ import annotations

from pydantic import TypeAdapter

from app.core.logging import get_logger
from app.domain.interfaces.cache import CacheService
from app.domain.interfaces.hotel import HotelProvider
from app.schemas.hotel import HotelOffer, HotelSearchCriteria

logger = get_logger(__name__)

_ADAPTER = TypeAdapter(list[HotelOffer])


def _cache_key(c: HotelSearchCriteria) -> str:
    return f"hotels:{c.destination.lower()}|{c.nights}|{c.guests}|{c.currency}"


class CachingHotelProvider(HotelProvider):
    """Adds read-through caching around another `HotelProvider`."""

    def __init__(
        self, inner: HotelProvider, cache: CacheService, ttl: int
    ) -> None:
        self._inner = inner
        self._cache = cache
        self._ttl = ttl

    async def search(self, criteria: HotelSearchCriteria) -> list[HotelOffer]:
        key = _cache_key(criteria)
        cached = await self._cache.get(key)
        if cached is not None:
            logger.info("cache.hit", key=key)
            return _ADAPTER.validate_json(cached)

        logger.info("cache.miss", key=key)
        offers = await self._inner.search(criteria)
        await self._cache.set(key, _ADAPTER.dump_json(offers).decode(), self._ttl)
        return offers
