"""Hotel endpoint — `POST /api/v1/hotels/search`.

Accepts the shared travel state and returns hotel offers plus the agent's
recommended selection.
"""

from fastapi import APIRouter, Depends

from app.agents.hotel import HotelAgent
from app.api.v1.dependencies import get_hotel_agent
from app.schemas.hotel import HotelSearchResponse
from app.schemas.trip import TripParameters

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.post(
    "/search",
    response_model=HotelSearchResponse,
    summary="Find hotels for a trip",
    description="Searches hotels (mock data for now) for the given travel "
    "state and returns offers plus a recommended selection.",
)
async def search_hotels(
    state: TripParameters,
    agent: HotelAgent = Depends(get_hotel_agent),
) -> HotelSearchResponse:
    return await agent.search(state)
