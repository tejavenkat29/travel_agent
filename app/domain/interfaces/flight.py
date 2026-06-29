"""Flight provider port (interface).

The abstraction the Flight Agent depends on. Any data source — the current
mock, or a future real API (Amadeus, Skyscanner, ...) — implements this single
method, making them fully interchangeable (Liskov) and letting new providers be
added without touching the agent (Open/Closed + Dependency Inversion).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.flight import FlightOffer, FlightSearchCriteria


class FlightProvider(ABC):
    """Source of flight offers for a normalised search query."""

    @abstractmethod
    async def search(self, criteria: FlightSearchCriteria) -> list[FlightOffer]:
        """Return available flight offers for the given criteria."""
        raise NotImplementedError
