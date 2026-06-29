"""Caching decorator for `WeatherProvider` (cache-aside)."""

from __future__ import annotations

from app.core.logging import get_logger
from app.domain.interfaces.cache import CacheService
from app.domain.interfaces.weather import WeatherProvider
from app.schemas.weather import WeatherForecast

logger = get_logger(__name__)


def _cache_key(destination: str) -> str:
    return f"weather:{destination.lower()}"


class CachingWeatherProvider(WeatherProvider):
    """Adds read-through caching around another `WeatherProvider`."""

    def __init__(
        self, inner: WeatherProvider, cache: CacheService, ttl: int
    ) -> None:
        self._inner = inner
        self._cache = cache
        self._ttl = ttl

    async def get_forecast(self, destination: str) -> WeatherForecast:
        key = _cache_key(destination)
        cached = await self._cache.get(key)
        if cached is not None:
            logger.info("cache.hit", key=key)
            return WeatherForecast.model_validate_json(cached)

        logger.info("cache.miss", key=key)
        forecast = await self._inner.get_forecast(destination)
        await self._cache.set(key, forecast.model_dump_json(), self._ttl)
        return forecast
