"""Final Response Agent.

The synthesizer: it receives every other agent's output and produces the final
deliverable in two forms —

  1. `TravelSummary`  — structured JSON, assembled deterministically from the
     agent outputs (reliable, machine-consumable).
  2. natural-language — a Markdown summary rendered deterministically from that
     same structure (consistent, "beautiful" formatting independent of LLM
     prose quality).

The only LLM-generated content is the creative part — recommendations and the
day-by-day itinerary — produced via an injected chain (testable with a stub).
"""

from __future__ import annotations

from langchain_core.runnables import Runnable

from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.schemas.flight import FlightOffer
from app.schemas.summary import (
    FinalResponse,
    FinalResponseRequest,
    ItineraryPlan,
    TravelSummary,
)

logger = get_logger(__name__)


def _select_flight(flights: list[FlightOffer]) -> FlightOffer | None:
    """Pick the best flight: cheapest within budget, else cheapest overall."""
    if not flights:
        return None
    within = [f for f in flights if f.within_budget]
    pool = within or flights
    return min(pool, key=lambda f: f.total_price)


def _weather_brief(req: FinalResponseRequest) -> str:
    """One-line weather context for the itinerary prompt."""
    if not req.weather:
        return "unknown"
    f = req.weather.forecast
    return (
        f"{f.condition}, {f.temp_low_c:.0f}-{f.temp_high_c:.0f}°C; "
        f"best seasons: {', '.join(req.weather.best_seasons)}"
    )


class FinalResponseAgent:
    """Composes the final travel summary (JSON + natural language)."""

    def __init__(self, itinerary_chain: Runnable) -> None:
        self._chain = itinerary_chain

    async def _generate_itinerary(
        self, req: FinalResponseRequest
    ) -> ItineraryPlan:
        try:
            return await self._chain.ainvoke(
                {
                    "destination": req.trip.destination or "the destination",
                    "source": req.trip.source or "home",
                    "num_days": req.trip.num_days or 3,
                    "travelers": req.trip.travelers or 1,
                    "weather": _weather_brief(req),
                }
            )
        except Exception as exc:
            logger.exception("final_response.itinerary_failed")
            raise ExternalServiceError(
                "Could not generate the itinerary.",
                code="itinerary_generation_failed",
            ) from exc

    async def compose(self, req: FinalResponseRequest) -> FinalResponse:
        itinerary = await self._generate_itinerary(req)
        flight = _select_flight(req.flights)

        summary = TravelSummary(
            destination=req.trip.destination,
            source=req.trip.source,
            travelers=req.trip.travelers or 1,
            num_days=req.trip.num_days or len(itinerary.daily_itinerary) or 1,
            currency=req.trip.currency
            or (req.budget.currency if req.budget else "USD"),
            flight=flight,
            hotel=req.hotel,
            weather=req.weather,
            budget=req.budget,
            recommendations=itinerary.recommendations,
            daily_itinerary=itinerary.daily_itinerary,
        )
        logger.info("final_response.composed", destination=summary.destination)
        return FinalResponse(
            summary=summary, natural_language=render_travel_markdown(summary)
        )


def render_travel_markdown(s: TravelSummary) -> str:
    """Render a TravelSummary as a clean, sectioned Markdown document."""
    L: list[str] = []
    cur = s.currency

    # --- Header ---
    L.append(f"# 🌍 Your Trip to {s.destination or 'your destination'}")
    meta = []
    if s.source:
        meta.append(f"from **{s.source}**")
    meta.append(f"**{s.num_days}** day(s)")
    meta.append(f"**{s.travelers}** traveler(s)")
    if s.budget and s.budget.user_budget is not None:
        meta.append(f"budget **{cur} {s.budget.user_budget:,.0f}**")
    L.append(" · ".join(meta))

    # --- Flight ---
    L.append("\n## ✈️ Flight")
    if s.flight:
        f = s.flight
        L.append(
            f"| Airline | Flight | Route | Depart | Arrive | Stops | Price |"
        )
        L.append("|---|---|---|---|---|---|---|")
        stops = "Direct" if f.stops == 0 else f"{f.stops} stop(s)"
        L.append(
            f"| {f.airline} | {f.flight_number} | {f.origin} → {f.destination} "
            f"| {f.departure_time} | {f.arrival_time} | {stops} "
            f"| {f.currency} {f.total_price:,.2f} |"
        )
    else:
        L.append("_No flight selected yet._")

    # --- Hotel ---
    L.append("\n## 🏨 Hotel")
    if s.hotel:
        h = s.hotel
        stars = f" ({h.rating}★)" if h.rating else ""
        area = f", {h.area}" if h.area else ""
        L.append(f"- **{h.name}**{stars}{area}")
        L.append(
            f"- {h.currency} {h.nightly_rate:,.2f}/night × {h.nights} nights "
            f"= **{h.currency} {h.total_price:,.2f}**"
        )
    else:
        L.append("_Hotel to be selected._")

    # --- Weather ---
    L.append("\n## 🌤️ Weather & What to Pack")
    if s.weather:
        w = s.weather
        L.append(
            f"- **{w.forecast.condition}**, "
            f"{w.forecast.temp_low_c:.0f}–{w.forecast.temp_high_c:.0f}°C"
        )
        L.append(f"- 🗓️ {w.best_time_to_visit}")
        if w.clothing_suggestions:
            L.append("- **Pack:**")
            L.extend(f"  - {tip}" for tip in w.clothing_suggestions)
    else:
        L.append("_Weather information unavailable._")

    # --- Budget ---
    L.append("\n## 💰 Budget")
    if s.budget:
        b = s.budget
        L.append("| Category | Amount | Basis |")
        L.append("|---|---|---|")
        for item in b.breakdown.line_items:
            kind = "est." if item.estimated else "actual"
            L.append(
                f"| {item.category.title()} | {cur} {item.amount:,.2f} "
                f"| {item.detail} ({kind}) |"
            )
        L.append(f"| **Total** | **{cur} {b.total_cost:,.2f}** | |")
        if b.within_budget is not None:
            verdict = "✅ within budget" if b.within_budget else "⚠️ over budget"
            L.append(f"\n**{verdict}** — {b.summary}")
    else:
        L.append("_Budget not calculated._")

    # --- Recommendations ---
    if s.recommendations:
        L.append("\n## 💡 Recommendations")
        L.extend(f"- {r}" for r in s.recommendations)

    # --- Daily itinerary ---
    if s.daily_itinerary:
        L.append("\n## 🗓️ Daily Itinerary")
        for day in s.daily_itinerary:
            L.append(f"\n**Day {day.day} — {day.title}**")
            L.extend(f"- {act}" for act in day.activities)

    return "\n".join(L)


def build_final_response_agent_from_settings(settings) -> FinalResponseAgent:
    """Build the Final Response Agent with the itinerary chain."""
    from app.agents.chains.itinerary_chain import (
        build_itinerary_chain_from_settings,
    )

    return FinalResponseAgent(build_itinerary_chain_from_settings(settings))
