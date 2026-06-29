"""Mock hotel provider.

Implements `HotelProvider` with deterministic synthetic offers derived from the
destination — no API key, stable output. Returns raw offers (per-night rates);
the agent selects the best one and computes trip totals.
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.domain.interfaces.hotel import HotelProvider
from app.schemas.hotel import HotelOffer, HotelSearchCriteria

logger = get_logger(__name__)

# (name, area, rating, nightly multiplier, amenities)
_TEMPLATES = [
    ("Grand Plaza Hotel", "City Center", 4.6, 1.6, ["WiFi", "Pool", "Gym"]),
    ("Riverside Suites", "Riverside", 4.3, 1.2, ["WiFi", "Breakfast"]),
    ("Budget Stay Inn", "Suburb", 3.8, 0.7, ["WiFi"]),
    ("Boutique Nest", "Old Town", 4.8, 1.9, ["WiFi", "Spa", "Breakfast", "Bar"]),
]


def _seed(destination: str) -> int:
    return sum(ord(c) for c in destination.lower())


class MockHotelProvider(HotelProvider):
    """Returns synthetic but plausible hotel offers."""

    async def search(self, criteria: HotelSearchCriteria) -> list[HotelOffer]:
        seed = _seed(criteria.destination)
        base_nightly = 60 + (seed % 140)  # 60..199
        logger.info(
            "hotels.mock_search",
            destination=criteria.destination,
            base_nightly=base_nightly,
        )
        return [
            HotelOffer(
                name=name,
                area=area,
                rating=rating,
                nightly_rate=round(base_nightly * mult, 2),
                currency=criteria.currency,
                amenities=amenities,
            )
            for name, area, rating, mult, amenities in _TEMPLATES
        ]
