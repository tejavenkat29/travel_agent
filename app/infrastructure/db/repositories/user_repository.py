"""User repository."""

from __future__ import annotations

from sqlalchemy import select

from app.infrastructure.db.models.user import User
from app.infrastructure.db.repositories.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User]):
    """CRUD + lookups for `User`."""

    model = User

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
