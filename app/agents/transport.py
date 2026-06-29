"""Transport Agent — multi-modal, validated.

Compares flight, train and bus for a route and recommends the cheapest feasible
option. Crucially, it **validates feasibility**: a flight is only offered when
both ends have an airport; otherwise it explains why and suggests the nearest
airport, so the planner never invents impossible routes (e.g. a flight from a
town with no airport).

Prices/durations are deterministic *simulated estimates* for demonstration — the
disclaimer says so. Replace the estimators with real APIs (Amadeus / IRCTC /
RedBus) for live data without changing the agent's interface.
"""

from __future__ import annotations

from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.core.observability import traceable
from app.infrastructure.data.transport_data import (
    BOOKING_APPS,
    has_airport,
    nearest_airport,
)
from app.schemas.transport import TransportComparison, TransportMode, TransportOption
from app.schemas.trip import TripParameters

logger = get_logger(__name__)

# Rough currency factors vs INR (indicative only).
_CCY_FACTOR = {"INR": 1.0, "USD": 1 / 83, "EUR": 1 / 90, "GBP": 1 / 105}

DISCLAIMER = (
    "Prices, operators and durations are simulated estimates for demonstration. "
    "Connect real APIs — Amadeus (flights), IRCTC/RailYatri (trains), "
    "RedBus/AbhiBus (buses) — for live availability and fares."
)


def _seed(a: str, b: str) -> int:
    return sum(ord(c) for c in f"{a}{b}".lower())


class TransportAgent:
    """Builds a validated flight/train/bus comparison for a trip."""

    @traceable(run_type="chain", name="transport_agent")
    async def compare(self, state: TripParameters) -> TransportComparison:
        if not state.source or not state.destination:
            raise ValidationError(
                "Both 'source' and 'destination' are required.",
                code="missing_route",
            )

        origin, dest = state.source, state.destination
        travelers = state.travelers or 1
        currency = (state.currency or "INR").upper()
        factor = _CCY_FACTOR.get(currency, 1.0)
        dist = 1 + (_seed(origin, dest) % 20)  # 1..20 distance proxy

        def money(inr: float) -> float:
            return round(inr * factor, 2)

        options: list[TransportOption] = []

        # --- Flight: only if BOTH ends have an airport ---
        origin_air, dest_air = has_airport(origin), has_airport(dest)
        if origin_air and dest_air:
            fare = 1200 + 350 * dist
            options.append(
                TransportOption(
                    mode=TransportMode.FLIGHT,
                    available=True,
                    provider="IndiGo / Air India (indicative)",
                    price_per_person=money(fare),
                    total_price=money(fare * travelers),
                    currency=currency,
                    duration_hours=round(1 + dist * 0.12, 1),
                    booking_apps=BOOKING_APPS["flight"],
                )
            )
        else:
            missing = origin if not origin_air else dest
            near = nearest_airport(missing)
            note = f"No commercial airport at {missing}."
            note += (
                f" Nearest airport: {near}. Fly there, then continue by road/rail."
                if near
                else " Travel by train or bus instead."
            )
            options.append(
                TransportOption(
                    mode=TransportMode.FLIGHT,
                    available=False,
                    currency=currency,
                    booking_apps=BOOKING_APPS["flight"],
                    note=note,
                )
            )

        # --- Train (assumed available between Indian cities) ---
        train_fare = 200 * dist
        options.append(
            TransportOption(
                mode=TransportMode.TRAIN,
                available=True,
                provider="Indian Railways (indicative)",
                price_per_person=money(train_fare),
                total_price=money(train_fare * travelers),
                currency=currency,
                duration_hours=round(2 + dist * 0.6, 1),
                booking_apps=BOOKING_APPS["train"],
            )
        )

        # --- Bus ---
        bus_fare = 120 * dist
        options.append(
            TransportOption(
                mode=TransportMode.BUS,
                available=True,
                provider="State RTC / private (indicative)",
                price_per_person=money(bus_fare),
                total_price=money(bus_fare * travelers),
                currency=currency,
                duration_hours=round(2.5 + dist * 0.8, 1),
                booking_apps=BOOKING_APPS["bus"],
            )
        )

        # --- Recommend the cheapest available option ---
        affordable = [o for o in options if o.available and o.total_price is not None]
        recommended = (
            min(affordable, key=lambda o: o.total_price) if affordable else None
        )

        if not (origin_air and dest_air):
            advisory = (
                "Flights aren't directly available for this route. "
                f"Recommended: {recommended.mode.value if recommended else 'train/bus'}"
                " (lowest cost)."
            )
        else:
            advisory = (
                f"Recommended: {recommended.mode.value} (lowest total cost)."
                if recommended
                else "No options available."
            )

        logger.info(
            "transport.compared",
            origin=origin,
            destination=dest,
            recommended=recommended.mode.value if recommended else None,
        )
        return TransportComparison(
            origin=origin,
            destination=dest,
            travelers=travelers,
            currency=currency,
            options=options,
            recommended=recommended,
            advisory=advisory,
            disclaimer=DISCLAIMER,
        )


def build_transport_agent_from_settings(_settings) -> TransportAgent:
    return TransportAgent()
