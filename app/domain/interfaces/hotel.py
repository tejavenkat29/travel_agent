"""Hotel provider port (interface).

The abstraction the Hotel Agent depends on. The mock and any future real API
(Booking.com, Amadeus Hotels, ...) implement this one method, so providers are
interchangeable and added without touching the agent.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.hotel import HotelOffer, HotelSearchCriteria


class HotelProvider(ABC):
    """Source of hotel offers for a normalised search query."""

    @abstractmethod
    async def search(self, criteria: HotelSearchCriteria) -> list[HotelOffer]:
        """Return available hotel offers for the given criteria."""
        raise NotImplementedError
