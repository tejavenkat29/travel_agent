"""Caching decorator for `FlightProvider`.

Wraps any inner provider and serves results from the cache when present
(cache-aside / lazy loading). Implements `FlightProvider` itself, so it is a
drop-in substitute (Liskov) selected by the factory.
"""

from __future__ import annotations

from pydantic import TypeAdapter

from app.core.logging import get_logger
from app.domain.interfaces.cache import CacheService
from app.domain.interfaces.flight import FlightProvider
from app.schemas.flight import FlightOffer, FlightSearchCriteria

logger = get_logger(__name__)

_ADAPTER = TypeAdapter(list[FlightOffer])


def _cache_key(c: FlightSearchCriteria) -> str:
    return f"flights:{c.origin.lower()}|{c.destination.lower()}|{c.passengers}|{c.currency}"


class CachingFlightProvider(FlightProvider):
    """Adds read-through caching around another `FlightProvider`."""

    def __init__(
        self, inner: FlightProvider, cache: CacheService, ttl: int
    ) -> None:
        self._inner = inner
        self._cache = cache
        self._ttl = ttl

    async def search(self, criteria: FlightSearchCriteria) -> list[FlightOffer]:
        key = _cache_key(criteria)
        cached = await self._cache.get(key)
        if cached is not None:
            logger.info("cache.hit", key=key)
            return _ADAPTER.validate_json(cached)

        logger.info("cache.miss", key=key)
        offers = await self._inner.search(criteria)
        await self._cache.set(key, _ADAPTER.dump_json(offers).decode(), self._ttl)
        return offers
