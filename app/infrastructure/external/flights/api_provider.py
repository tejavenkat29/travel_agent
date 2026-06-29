"""Real flight-API provider (skeleton).

Placeholder implementation of `FlightProvider` for a live flight API (e.g.
Amadeus, Skyscanner, Kiwi). It demonstrates the Open/Closed principle: when a
real integration is needed, fill in `search()` here and select it in the
factory — no other code (agent, endpoint, schemas) changes.
"""

from __future__ import annotations

import httpx

from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.domain.interfaces.flight import FlightProvider
from app.schemas.flight import FlightOffer, FlightSearchCriteria

logger = get_logger(__name__)


class ApiFlightProvider(FlightProvider):
    """Fetches live offers from an external flight API."""

    def __init__(self, api_key: str, base_url: str = "https://api.example-flights.com"):
        self._api_key = api_key
        self._base_url = base_url

    async def search(self, criteria: FlightSearchCriteria) -> list[FlightOffer]:
        # TODO: implement the real integration. Sketch of the intended shape:
        #
        # async with httpx.AsyncClient(base_url=self._base_url) as client:
        #     resp = await client.get(
        #         "/v1/flights",
        #         params={
        #             "origin": criteria.origin,
        #             "destination": criteria.destination,
        #             "adults": criteria.passengers,
        #             "currency": criteria.currency,
        #         },
        #         headers={"Authorization": f"Bearer {self._api_key}"},
        #     )
        #     resp.raise_for_status()
        #     return [_to_offer(item) for item in resp.json()["data"]]
        #
        # The only responsibility here is mapping the provider's payload into
        # our `FlightOffer` shape — the agent stays unchanged.
        _ = httpx  # referenced to make the intended dependency explicit
        raise ExternalServiceError(
            "Live flight API provider is not implemented yet.",
            code="flight_provider_unavailable",
        )
