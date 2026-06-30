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

# (name suffix, area, rating, nightly multiplier, amenities)
_TEMPLATES = [
    ("Grand Plaza", "City Center", 4.6, 1.6, ["WiFi", "Pool", "Gym"]),
    ("Riverside Suites", "Riverside", 4.3, 1.2, ["WiFi", "Breakfast"]),
    ("OYO Townhouse", "Suburb", 3.8, 0.7, ["WiFi"]),
    ("Boutique Nest", "Old Town", 4.8, 1.9, ["WiFi", "Spa", "Breakfast", "Bar"]),
    ("Comfort Inn", "Near Station", 4.0, 0.9, ["WiFi", "Breakfast"]),
]

# Rough INR->other conversion so non-INR trips still get sane numbers.
_CCY_FACTOR = {"INR": 1.0, "USD": 1 / 83, "EUR": 1 / 90, "GBP": 1 / 105}


def _seed(destination: str) -> int:
    return sum(ord(c) for c in destination.lower())


class MockHotelProvider(HotelProvider):
    """Returns synthetic but plausible hotel offers (INR-based, location-tagged)."""

    async def search(self, criteria: HotelSearchCriteria) -> list[HotelOffer]:
        seed = _seed(criteria.destination)
        # Realistic INR nightly base: ~₹1,400–4,000 before the per-tier multiplier.
        base_inr = 1400 + (seed % 2600)
        factor = _CCY_FACTOR.get(criteria.currency.upper(), 1.0)
        city = criteria.destination.strip().title()
        logger.info(
            "hotels.mock_search", destination=criteria.destination, base_inr=base_inr
        )
        return [
            HotelOffer(
                name=f"{city} {suffix}",
                area=area,
                rating=rating,
                nightly_rate=round(base_inr * mult * factor, 2),
                currency=criteria.currency,
                amenities=amenities,
            )
            for suffix, area, rating, mult, amenities in _TEMPLATES
        ]
