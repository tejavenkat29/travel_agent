"""Repository port (interface).

The persistence abstraction the application depends on. It declares the CRUD
contract generically (over a `ModelT`) without importing any ORM or database
code, so use cases/routes depend on the contract, not on SQLAlchemy. Concrete
implementations live in the infrastructure layer (Dependency Inversion).
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

ModelT = TypeVar("ModelT")


class AbstractRepository(ABC, Generic[ModelT]):
    """Generic CRUD contract for a persistent entity."""

    @abstractmethod
    async def create(self, **data) -> ModelT: ...

    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> ModelT | None: ...

    @abstractmethod
    async def list(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, **data) -> ModelT | None: ...

    @abstractmethod
    async def delete(self, entity_id: uuid.UUID) -> bool: ...
