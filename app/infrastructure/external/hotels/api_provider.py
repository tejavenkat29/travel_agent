"""Real hotel-API provider (skeleton).

Placeholder `HotelProvider` for a live hotel API (e.g. Booking.com, Amadeus
Hotels, Hotelbeds). Implement `search()` here and select it in the factory —
the agent, endpoint and schemas stay unchanged (Open/Closed).
"""

from __future__ import annotations

import httpx

from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.domain.interfaces.hotel import HotelProvider
from app.schemas.hotel import HotelOffer, HotelSearchCriteria

logger = get_logger(__name__)


class ApiHotelProvider(HotelProvider):
    """Fetches live hotel offers from an external API."""

    def __init__(self, api_key: str, base_url: str = "https://api.example-hotels.com"):
        self._api_key = api_key
        self._base_url = base_url

    async def search(self, criteria: HotelSearchCriteria) -> list[HotelOffer]:
        # TODO: implement the real integration; map the provider payload into
        # `HotelOffer`. The agent's selection logic stays unchanged.
        _ = httpx
        raise ExternalServiceError(
            "Live hotel API provider is not implemented yet.",
            code="hotel_provider_unavailable",
        )
