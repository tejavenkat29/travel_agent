"""Flight provider factory.

Centralises the choice of `FlightProvider` implementation. Selection is driven
by configuration: when `FLIGHTS_API_KEY` is set the live API provider is used,
otherwise the deterministic mock. The agent never knows which one it got — it
only sees the `FlightProvider` abstraction (Dependency Inversion).
"""

from __future__ import annotations

from app.core.config import Settings
from app.core.logging import get_logger
from app.domain.interfaces.flight import FlightProvider
from app.infrastructure.external.flights.mock_provider import MockFlightProvider

logger = get_logger(__name__)


def build_flight_provider(settings: Settings) -> FlightProvider:
    """Return the configured flight provider (live if keyed, else mock).

    When caching is enabled, the chosen provider is wrapped in a read-through
    caching decorator — transparent to the agent.
    """
    if settings.FLIGHTS_API_KEY:
        from app.infrastructure.external.flights.api_provider import (
            ApiFlightProvider,
        )

        logger.info("flights.provider_selected", provider="api")
        provider: FlightProvider = ApiFlightProvider(api_key=settings.FLIGHTS_API_KEY)
    else:
        logger.info("flights.provider_selected", provider="mock")
        provider = MockFlightProvider()

    if settings.CACHE_ENABLED:
        from app.infrastructure.cache.factory import get_cache_service
        from app.infrastructure.external.flights.caching_provider import (
            CachingFlightProvider,
        )

        provider = CachingFlightProvider(
            provider, get_cache_service(), settings.CACHE_TTL_FLIGHTS
        )
    return provider
