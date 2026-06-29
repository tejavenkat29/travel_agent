"""Generic SQLAlchemy repository.

Implements the `AbstractRepository` CRUD contract once, against any ORM model.
Concrete repositories just set `model` and add entity-specific queries. Writes
`flush()` (to assign PKs / surface constraint errors) but do NOT commit — the
unit of work (`get_db`) owns the transaction boundary.
"""

from __future__ import annotations

import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.repository import AbstractRepository

ModelT = TypeVar("ModelT")


class SQLAlchemyRepository(AbstractRepository[ModelT], Generic[ModelT]):
    """Reusable CRUD implementation for a single model."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **data) -> ModelT:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def get(self, entity_id: uuid.UUID) -> ModelT | None:
        return await self.session.get(self.model, entity_id)

    async def list(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]:
        result = await self.session.execute(
            select(self.model)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update(self, entity_id: uuid.UUID, **data) -> ModelT | None:
        obj = await self.get(entity_id)
        if obj is None:
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, entity_id: uuid.UUID) -> bool:
        obj = await self.get(entity_id)
        if obj is None:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True
