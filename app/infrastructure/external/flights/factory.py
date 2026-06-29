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
    """Return the configured flight provider (live if keyed, else mock)."""
    if settings.FLIGHTS_API_KEY:
        from app.infrastructure.external.flights.api_provider import (
            ApiFlightProvider,
        )

        logger.info("flights.provider_selected", provider="api")
        return ApiFlightProvider(api_key=settings.FLIGHTS_API_KEY)

    logger.info("flights.provider_selected", provider="mock")
    return MockFlightProvider()
