"""Transport endpoint — `POST /api/v1/transport/compare`.

Returns a validated flight/train/bus comparison with a recommendation and
booking-app suggestions for the given travel state.
"""

from fastapi import APIRouter, Depends

from app.agents.transport import TransportAgent
from app.api.v1.dependencies import get_transport_agent
from app.schemas.transport import TransportComparison
from app.schemas.trip import TripParameters

router = APIRouter(prefix="/transport", tags=["transport"])


@router.post(
    "/compare",
    response_model=TransportComparison,
    summary="Compare flight/train/bus for a trip",
    description="Validates feasibility (e.g. airport availability), compares "
    "modes, recommends the cheapest, and suggests booking apps.",
)
async def compare_transport(
    state: TripParameters,
    agent: TransportAgent = Depends(get_transport_agent),
) -> TransportComparison:
    return await agent.compare(state)
