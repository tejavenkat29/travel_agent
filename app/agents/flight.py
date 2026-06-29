"""Flight Agent.

Consumes the shared travel state (`TripParameters`) and returns available
flights. Its single responsibility is *orchestration*: translate the trip brief
into a `FlightSearchCriteria`, ask the injected `FlightProvider` for offers,
then sort and annotate them against the budget. It performs no I/O itself and
knows nothing about where the data comes from (Dependency Inversion) — so the
mock and a real API are drop-in interchangeable.
"""

from __future__ import annotations

from app.core.exceptions import ExternalServiceError, ValidationError
from app.core.logging import get_logger
from app.domain.interfaces.flight import FlightProvider
from app.schemas.flight import FlightOffer, FlightSearchCriteria
from app.schemas.trip import TripParameters

logger = get_logger(__name__)


class FlightAgent:
    """Finds and ranks flight offers for a trip."""

    def __init__(self, provider: FlightProvider) -> None:
        self._provider = provider

    def _build_criteria(self, state: TripParameters) -> FlightSearchCriteria:
        if not state.source or not state.destination:
            raise ValidationError(
                "Both 'source' and 'destination' are required to search flights.",
                code="missing_route",
            )
        return FlightSearchCriteria(
            origin=state.source,
            destination=state.destination,
            passengers=state.travelers or 1,
            currency=state.currency or "USD",
        )

    async def find_flights(self, state: TripParameters) -> list[FlightOffer]:
        criteria = self._build_criteria(state)
        try:
            offers = await self._provider.search(criteria)
        except ExternalServiceError:
            raise  # already a clean application error
        except Exception as exc:  # normalise unexpected provider failures
            logger.exception("flights.search_failed")
            raise ExternalServiceError(
                "The flight provider failed to return offers.",
                code="flight_search_failed",
            ) from exc

        # Cheapest first.
        offers.sort(key=lambda o: o.total_price)
        # Annotate each offer against the trip budget, when known.
        if state.budget is not None:
            for offer in offers:
                offer.within_budget = offer.total_price <= state.budget

        logger.info("flights.found", count=len(offers))
        return offers


def build_flight_agent_from_settings(settings) -> FlightAgent:
    """Build the Flight Agent with the configured provider."""
    from app.infrastructure.external.flights.factory import build_flight_provider

    return FlightAgent(build_flight_provider(settings))
