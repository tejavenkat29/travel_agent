"""Hotel provider factory.

Selects the `HotelProvider` from configuration: live API when `HOTELS_API_KEY`
is set, otherwise the deterministic mock. The agent only sees the abstraction.
"""

from __future__ import annotations

from app.core.config import Settings
from app.core.logging import get_logger
from app.domain.interfaces.hotel import HotelProvider
from app.infrastructure.external.hotels.mock_provider import MockHotelProvider

logger = get_logger(__name__)


def build_hotel_provider(settings: Settings) -> HotelProvider:
    """Return the configured hotel provider (live if keyed, else mock)."""
    api_key = getattr(settings, "HOTELS_API_KEY", None)
    if api_key:
        from app.infrastructure.external.hotels.api_provider import ApiHotelProvider

        logger.info("hotels.provider_selected", provider="api")
        return ApiHotelProvider(api_key=api_key)

    logger.info("hotels.provider_selected", provider="mock")
    return MockHotelProvider()
