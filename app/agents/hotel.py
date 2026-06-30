"""Hotel Agent.

Consumes the shared travel state, asks the injected `HotelProvider` for offers,
then *selects* the best-value hotel and computes trip-specific totals
(nightly rate x nights). Provider = raw data; agent = selection + math (SRP).
"""

from __future__ import annotations

from app.core.exceptions import ExternalServiceError, ValidationError
from app.core.logging import get_logger
from app.core.observability import traceable
from app.domain.interfaces.hotel import HotelProvider
from app.schemas.hotel import (
    HotelInfo,
    HotelOffer,
    HotelSearchCriteria,
    HotelSearchResponse,
)
from app.schemas.trip import TripParameters

logger = get_logger(__name__)


def _select_best(offers: list[HotelOffer]) -> HotelOffer | None:
    """Best value: highest rating, cheaper wins ties."""
    if not offers:
        return None
    return max(offers, key=lambda h: (h.rating, -h.nightly_rate))


class HotelAgent:
    """Finds hotels and recommends the best option for a trip."""

    def __init__(self, provider: HotelProvider) -> None:
        self._provider = provider

    def _build_criteria(self, state: TripParameters) -> HotelSearchCriteria:
        if not state.destination:
            raise ValidationError(
                "A 'destination' is required to search hotels.",
                code="missing_destination",
            )
        return HotelSearchCriteria(
            destination=state.destination,
            nights=state.num_days or 1,
            guests=state.travelers or 1,
            currency=state.currency or "INR",
        )

    @traceable(run_type="chain", name="hotel_agent")
    async def search(self, state: TripParameters) -> HotelSearchResponse:
        criteria = self._build_criteria(state)
        try:
            offers = await self._provider.search(criteria)
        except ExternalServiceError:
            raise
        except Exception as exc:
            logger.exception("hotels.search_failed")
            raise ExternalServiceError(
                "The hotel provider failed to return offers.",
                code="hotel_search_failed",
            ) from exc

        offers.sort(key=lambda h: h.rating, reverse=True)
        best = _select_best(offers)
        selected = (
            HotelInfo(
                name=best.name,
                area=best.area,
                rating=best.rating,
                nightly_rate=best.nightly_rate,
                nights=criteria.nights,
                total_price=round(best.nightly_rate * criteria.nights, 2),
                currency=best.currency,
            )
            if best
            else None
        )
        logger.info("hotels.selected", hotel=selected.name if selected else None)
        return HotelSearchResponse(
            destination=criteria.destination,
            nights=criteria.nights,
            currency=criteria.currency,
            count=len(offers),
            selected=selected,
            offers=offers,
        )

    async def find_hotel(self, state: TripParameters) -> HotelInfo | None:
        """Convenience: return just the recommended hotel (used by the graph)."""
        return (await self.search(state)).selected


def build_hotel_agent_from_settings(settings) -> HotelAgent:
    """Build the Hotel Agent with the configured provider."""
    from app.infrastructure.external.hotels.factory import build_hotel_provider

    return HotelAgent(build_hotel_provider(settings))
