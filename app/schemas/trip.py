"""Trip schemas — the Planner Agent's structured output.

`TripParameters` is the canonical "trip brief": the structured representation
of what the user asked for. It plays three roles:
  1. the **target schema** for LangChain structured output (the LLM is forced
     to return data matching it),
  2. the **API response** of the planner endpoint, and
  3. the shared input the downstream agents (flights, hotels, budget) will read.

Every field is Optional because a user request rarely states everything; the
agent is instructed to leave unknowns as null rather than invent them. The
field `description`s double as extraction guidance for the LLM.
"""

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    """Input for the planner endpoint — the raw user request."""

    request: str = Field(
        ...,
        min_length=3,
        description="Natural-language travel request from the user",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "request": "Plan a 5 day trip from Mumbai to Tokyo for 2 "
                "people with a budget of around $4000."
            }
        }
    }


class TripParameters(BaseModel):
    """Structured trip parameters extracted from a free-text request."""

    destination: str | None = Field(
        default=None, description="Where the user wants to travel TO (city/country)"
    )
    source: str | None = Field(
        default=None,
        description="Where the user is travelling FROM (origin city/country)",
    )
    budget: float | None = Field(
        default=None, description="Total trip budget as a number, if stated"
    )
    currency: str | None = Field(
        default=None,
        description="ISO-like currency code for the budget, e.g. USD, EUR, INR",
    )
    num_days: int | None = Field(
        default=None, description="Trip duration in days, if stated"
    )
    travelers: int | None = Field(
        default=None, description="Number of people travelling, if stated"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "destination": "Tokyo",
                "source": "Mumbai",
                "budget": 4000,
                "currency": "USD",
                "num_days": 5,
                "travelers": 2,
            }
        }
    }
