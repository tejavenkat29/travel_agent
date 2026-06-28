"""Travel-assistant endpoint — `POST /api/v1/travel/assistant`.

Thin presentation handler: validates the request, delegates to the
`TravelAssistantUseCase`, and returns the structured `TravelRecommendation`.
"""

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_travel_assistant
from app.schemas.travel import TravelAssistantRequest, TravelRecommendation
from app.use_cases.travel_assistant import TravelAssistantUseCase

router = APIRouter(prefix="/travel", tags=["travel"])


@router.post(
    "/assistant",
    response_model=TravelRecommendation,
    summary="Get a structured travel recommendation",
    description="Runs a LangChain `prompt | model | parser` chain and returns "
    "a validated destination recommendation.",
)
async def travel_assistant(
    request: TravelAssistantRequest,
    use_case: TravelAssistantUseCase = Depends(get_travel_assistant),
) -> TravelRecommendation:
    return await use_case.recommend(
        query=request.query,
        duration_days=request.duration_days,
        budget_usd=request.budget_usd,
    )
