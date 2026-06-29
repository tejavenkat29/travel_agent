"""Final summary endpoint — `POST /api/v1/summary/compose`.

Receives the collected outputs from all agents and returns the final travel
summary as structured JSON plus a natural-language Markdown response.
"""

from fastapi import APIRouter, Depends

from app.agents.final_response import FinalResponseAgent
from app.api.v1.dependencies import get_final_response_agent
from app.schemas.summary import FinalResponse, FinalResponseRequest

router = APIRouter(prefix="/summary", tags=["summary"])


@router.post(
    "/compose",
    response_model=FinalResponse,
    summary="Compose the final travel summary (JSON + natural language)",
    description="Synthesizes flight, hotel, weather and budget outputs with an "
    "LLM-generated itinerary into a single structured + Markdown summary.",
)
async def compose_summary(
    body: FinalResponseRequest,
    agent: FinalResponseAgent = Depends(get_final_response_agent),
) -> FinalResponse:
    return await agent.compose(body)
