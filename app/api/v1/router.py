"""Version 1 API aggregator.

Collects all `v1` route modules under a single `APIRouter`, which `app.main`
mounts at the `API_V1_PREFIX` (default `/api/v1`). Business endpoints (trip
planning, itineraries, agent runs) will register their routers here as they are
implemented — keeping the versioned surface in one place.
"""

from fastapi import APIRouter

from app.api.v1.routes import chat

api_router = APIRouter()
api_router.include_router(chat.router)

# Further business routers are included here as they are built, e.g.:
#   from app.api.v1.routes import trips
#   api_router.include_router(trips.router, prefix="/trips", tags=["trips"])
