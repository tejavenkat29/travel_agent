"""Concurrency regression test for the LangGraph workflow.

Proves the optimization contract:
- Flight, Hotel and Weather nodes run **in parallel** (their execution
  intervals overlap), not sequentially.
- The Budget node is **synchronized** to start only after all three finish
  (the fan-in / join).
- Wall-clock for the parallel section is ~max(node) not sum(nodes).

Each stub agent awaits `DELAY` seconds; a wrapper records node start/end
timestamps so we can assert the timing relationships. Run with `pytest`.
"""

from __future__ import annotations

import asyncio
import time

from langchain_core.runnables import RunnableLambda

from app.agents.budget import BudgetAgent
from app.agents.chains.itinerary_chain import build_itinerary_chain
from app.agents.final_response import FinalResponseAgent
from app.agents.graph.nodes import TravelNodes
from app.agents.graph.workflow import build_travel_workflow
from app.schemas.hotel import HotelInfo, HotelOffer, HotelSearchResponse
from app.schemas.summary import DayPlan, ItineraryPlan
from app.schemas.transport import TransportComparison, TransportMode, TransportOption
from app.schemas.trip import TripParameters
from app.schemas.weather import SeasonOutlook, WeatherAdvisory, WeatherForecast

DELAY = 0.2  # seconds each parallel agent "works"


# --- Stub agents (await DELAY to simulate real I/O latency) -----------------
class StubPlanner:
    async def plan(self, _text: str) -> TripParameters:
        return TripParameters(
            destination="Tokyo", source="Mumbai", num_days=3,
            travelers=2, budget=4000, currency="USD",
        )


class SlowTransport:
    async def compare(self, _state):
        await asyncio.sleep(DELAY)
        bus = TransportOption(
            mode=TransportMode.BUS, available=True, provider="RTC",
            price_per_person=100, total_price=200, currency="USD",
            duration_hours=8, booking_apps=["RedBus"],
        )
        return TransportComparison(
            origin="Mumbai", destination="Tokyo", travelers=2, currency="USD",
            options=[bus], recommended=bus, advisory="ok", disclaimer="simulated",
        )


class SlowHotel:
    async def search(self, _state):
        await asyncio.sleep(DELAY)
        offer = HotelOffer(
            name="H", area="C", rating=4.0, nightly_rate=100,
            currency="USD", amenities=[],
        )
        selected = HotelInfo(
            name="H", area="C", rating=4.0, nightly_rate=100,
            nights=3, total_price=300, currency="USD",
        )
        return HotelSearchResponse(
            destination="Tokyo", nights=3, currency="USD",
            count=1, selected=selected, offers=[offer],
        )


class SlowWeather:
    async def advise(self, _destination):
        await asyncio.sleep(DELAY)
        return WeatherAdvisory(
            forecast=WeatherForecast(
                destination="Tokyo", condition="Sunny", temp_high_c=25,
                temp_low_c=15, humidity_pct=50, precipitation_chance_pct=10,
                wind_kph=10,
                seasonal_outlook=[
                    SeasonOutlook(season="Spring", avg_high_c=20, avg_low_c=12, note="n")
                ],
            ),
            clothing_suggestions=["light jacket"],
            best_seasons=["Spring"],
            best_time_to_visit="Spring",
        )


def _stub_final() -> FinalResponseAgent:
    class StubModel:
        def with_structured_output(self, _schema):
            return RunnableLambda(
                lambda _v: ItineraryPlan(
                    recommendations=["x"],
                    daily_itinerary=[DayPlan(day=i, title="d", activities=["a"]) for i in (1, 2, 3)],
                )
            )
    return FinalResponseAgent(build_itinerary_chain(StubModel()))


def _build_instrumented():
    """Build the workflow with timing wrappers around every node."""
    events: list[tuple[str, str, float]] = []
    nodes = TravelNodes(
        planner=StubPlanner(), transport=SlowTransport(), hotel=SlowHotel(),
        weather=SlowWeather(), budget=BudgetAgent(), final=_stub_final(),
    )

    def track(fn, name):
        async def wrapper(state):
            events.append((name, "start", time.perf_counter()))
            result = await fn(state)
            events.append((name, "end", time.perf_counter()))
            return result
        return wrapper

    for nm in ("planner", "transport", "hotel", "weather", "budget", "final"):
        method = f"{nm}_node"
        setattr(nodes, method, track(getattr(nodes, method), nm))

    return build_travel_workflow(nodes), events


def test_parallel_agents_overlap_and_budget_waits():
    workflow, events = _build_instrumented()

    t0 = time.perf_counter()
    asyncio.run(workflow.ainvoke({"user_request": "trip", "include_weather": True}))
    wall = time.perf_counter() - t0

    spans = {
        name: (
            next(t for n, p, t in events if n == name and p == "start"),
            next(t for n, p, t in events if n == name and p == "end"),
        )
        for name in ("transport", "hotel", "weather", "budget")
    }

    # 1) Parallel: the three intervals share a common instant.
    latest_start = max(spans[n][0] for n in ("transport", "hotel", "weather"))
    earliest_end = min(spans[n][1] for n in ("transport", "hotel", "weather"))
    assert latest_start < earliest_end, "transport/hotel/weather did not overlap"

    # 2) Synchronization: budget starts only after all three have finished.
    last_parallel_end = max(spans[n][1] for n in ("transport", "hotel", "weather"))
    assert spans["budget"][0] >= last_parallel_end - 1e-3, "budget started too early"

    # 3) Performance: parallel section ~= one DELAY, far below 3*DELAY.
    parallel_window = last_parallel_end - min(
        spans[n][0] for n in ("transport", "hotel", "weather")
    )
    assert parallel_window < 2 * DELAY, f"no speedup: {parallel_window:.3f}s"
    assert wall < 3 * DELAY, f"wall clock {wall:.3f}s looks sequential"


if __name__ == "__main__":
    test_parallel_agents_overlap_and_budget_waits()
    print("OK: parallel overlap + budget synchronization verified")
