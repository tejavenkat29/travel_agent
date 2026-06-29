"""Trip repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.infrastructure.db.models.trip import Trip
from app.infrastructure.db.repositories.base import SQLAlchemyRepository


class TripRepository(SQLAlchemyRepository[Trip]):
    """CRUD + lookups for `Trip`."""

    model = Trip

    async def list_by_user(
        self, user_id: uuid.UUID, *, limit: int = 100, offset: int = 0
    ) -> list[Trip]:
        result = await self.session.execute(
            select(Trip)
            .where(Trip.user_id == user_id)
            .order_by(Trip.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
