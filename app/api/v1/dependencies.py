"""FastAPI dependency-injection wiring.

Central place to declare reusable `Depends(...)` providers (DB sessions, Redis
client, LLM provider, current settings, authenticated user, ...). Concrete
providers are added as the infrastructure layer is implemented.
"""

from app.core.config import Settings, get_settings


def get_app_settings() -> Settings:
    """Expose validated settings to route handlers via DI."""
    return get_settings()
