"""Chat history repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.infrastructure.db.models.chat import ChatHistory
from app.infrastructure.db.repositories.base import SQLAlchemyRepository


class ChatHistoryRepository(SQLAlchemyRepository[ChatHistory]):
    """CRUD + lookups for `ChatHistory`."""

    model = ChatHistory

    async def list_by_trip(
        self, trip_id: uuid.UUID, *, limit: int = 200, offset: int = 0
    ) -> list[ChatHistory]:
        result = await self.session.execute(
            select(ChatHistory)
            .where(ChatHistory.trip_id == trip_id)
            .order_by(ChatHistory.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def list_by_user(
        self, user_id: uuid.UUID, *, limit: int = 200, offset: int = 0
    ) -> list[ChatHistory]:
        result = await self.session.execute(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
