"""Flight endpoint — `POST /api/v1/flights/search`.

Accepts the shared travel state (`TripParameters`) and returns ranked flight
offers via the Flight Agent.
"""

from fastapi import APIRouter, Depends

from app.agents.flight import FlightAgent
from app.api.v1.dependencies import get_flight_agent
from app.schemas.flight import FlightSearchResponse
from app.schemas.trip import TripParameters

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post(
    "/search",
    response_model=FlightSearchResponse,
    summary="Find available flights for a trip",
    description="Searches flights (mock data for now) for the given travel "
    "state and returns offers sorted cheapest-first.",
)
async def search_flights(
    state: TripParameters,
    agent: FlightAgent = Depends(get_flight_agent),
) -> FlightSearchResponse:
    offers = await agent.find_flights(state)
    return FlightSearchResponse(
        origin=state.source or "",
        destination=state.destination or "",
        passengers=state.travelers or 1,
        currency=state.currency or "USD",
        count=len(offers),
        offers=offers,
    )
