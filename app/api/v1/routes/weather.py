"""Weather endpoint — `POST /api/v1/weather/forecast`.

Takes a destination and returns the Weather Agent's advisory: forecast plus
clothing and best-time-to-visit guidance.
"""

from fastapi import APIRouter, Depends

from app.agents.weather import WeatherAgent
from app.api.v1.dependencies import get_weather_agent
from app.schemas.weather import WeatherAdvisory, WeatherRequest

router = APIRouter(prefix="/weather", tags=["weather"])


@router.post(
    "/forecast",
    response_model=WeatherAdvisory,
    summary="Get weather forecast and travel advice for a destination",
    description="Returns the forecast (mock data for now) plus clothing "
    "suggestions and the best time to visit.",
)
async def weather_forecast(
    body: WeatherRequest,
    agent: WeatherAgent = Depends(get_weather_agent),
) -> WeatherAdvisory:
    return await agent.advise(body.destination)
