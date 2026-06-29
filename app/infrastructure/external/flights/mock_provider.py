"""Mock flight provider.

Implements `FlightProvider` with deterministic, synthetic data so the whole
flight flow works end-to-end without any external dependency or API key. Output
is derived from the route (no randomness) so results are stable and testable.

Swapping this for a real API later requires no change to the agent — only a
different `FlightProvider` implementation (see `api_provider.py`).
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.domain.interfaces.flight import FlightProvider
from app.schemas.flight import FlightOffer, FlightSearchCriteria

logger = get_logger(__name__)

# (airline, flight prefix, fare multiplier, stops, departure, arrival, minutes)
_TEMPLATES = [
    ("IndiGo", "6E", 0.85, 1, "06:10", "18:40", 750),
    ("AirLink", "AL", 1.00, 1, "09:30", "22:15", 765),
    ("SkyJet", "SJ", 1.35, 0, "13:00", "21:20", 500),
    ("Premium Air", "PA", 1.90, 0, "20:45", "06:05", 560),
]


def _route_seed(origin: str, destination: str) -> int:
    """Stable pseudo-distance from the route text (deterministic)."""
    return sum(ord(c) for c in f"{origin}{destination}".lower())


class MockFlightProvider(FlightProvider):
    """Returns synthetic but realistic-looking flight offers."""

    async def search(self, criteria: FlightSearchCriteria) -> list[FlightOffer]:
        seed = _route_seed(criteria.origin, criteria.destination)
        base_fare = 120 + (seed % 600)  # 120..719
        logger.info(
            "flights.mock_search",
            origin=criteria.origin,
            destination=criteria.destination,
            base_fare=base_fare,
        )

        offers: list[FlightOffer] = []
        for i, (airline, prefix, mult, stops, dep, arr, mins) in enumerate(
            _TEMPLATES
        ):
            fare = round(base_fare * mult, 2)
            offers.append(
                FlightOffer(
                    airline=airline,
                    flight_number=f"{prefix}{100 + (seed + i) % 900}",
                    origin=criteria.origin,
                    destination=criteria.destination,
                    departure_time=dep,
                    arrival_time=arr,
                    duration_minutes=mins,
                    stops=stops,
                    fare_per_person=fare,
                    total_price=round(fare * criteria.passengers, 2),
                    currency=criteria.currency,
                    seats_available=3 + (seed + i) % 9,
                )
            )
        return offers
