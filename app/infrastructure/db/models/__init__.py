"""ORM models package.

Importing the models here ensures they are registered on `Base.metadata`, so
Alembic autogenerate and `create_all` see every table.
"""

from app.infrastructure.db.models.chat import ChatHistory
from app.infrastructure.db.models.trip import Trip
from app.infrastructure.db.models.user import User

__all__ = ["User", "Trip", "ChatHistory"]
