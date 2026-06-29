"""Travel-assistant schemas.

`TravelRecommendation` serves a dual role: it is the **target type for the
LangChain output parser** (the model must return JSON matching this schema) and
the **API response model**. Keeping one Pydantic definition avoids drift
between what the LLM produces and what the API promises.
"""

from pydantic import BaseModel, Field


class TravelAssistantRequest(BaseModel):
    """Body for `POST /travel/assistant`."""

    query: str = Field(
        ...,
        min_length=3,
        description="Free-text travel request, e.g. 'a relaxed beach trip'",
    )
    duration_days: int = Field(
        default=5, ge=1, le=60, description="Desired trip length in days"
    )
    budget_usd: float | None = Field(
        default=None, ge=0, description="Optional total budget in USD"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "a relaxed beach holiday with good food",
                "duration_days": 7,
                "budget_usd": 2000,
            }
        }
    }


class TravelRecommendation(BaseModel):
    """Structured travel recommendation (LLM output + API response)."""

    destination: str = Field(..., description="Recommended city or place")
    country: str = Field(..., description="Country of the destination")
    summary: str = Field(..., description="Why this destination fits the request")
    suggested_days: int = Field(..., description="Recommended number of days")
    highlights: list[str] = Field(
        ..., description="Key things to see or do (3-5 items)"
    )
    estimated_budget_usd: float | None = Field(
        default=None, description="Rough total cost estimate in USD, if known"
    )
