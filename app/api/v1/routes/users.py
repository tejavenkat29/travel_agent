"""User CRUD endpoints — `/api/v1/users`.

Demonstrates the repository pattern end-to-end: each handler gets a transactional
session via `get_db`, wraps it in a `UserRepository`, and performs one CRUD
operation. The session commits when the request succeeds (unit of work).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


@router.post(
    "", response_model=UserRead, status_code=status.HTTP_201_CREATED,
    summary="Create a user",
)
async def create_user(
    body: UserCreate, repo: UserRepository = Depends(get_user_repository)
) -> UserRead:
    if await repo.get_by_email(body.email):
        raise ConflictError("A user with this email already exists.")
    user = await repo.create(email=body.email, full_name=body.full_name)
    return UserRead.model_validate(user)


@router.get("", response_model=list[UserRead], summary="List users")
async def list_users(
    limit: int = 100,
    offset: int = 0,
    repo: UserRepository = Depends(get_user_repository),
) -> list[UserRead]:
    users = await repo.list(limit=limit, offset=offset)
    return [UserRead.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserRead, summary="Get a user")
async def get_user(
    user_id: uuid.UUID, repo: UserRepository = Depends(get_user_repository)
) -> UserRead:
    user = await repo.get(user_id)
    if user is None:
        raise NotFoundError("User not found.")
    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead, summary="Update a user")
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    repo: UserRepository = Depends(get_user_repository),
) -> UserRead:
    user = await repo.update(
        user_id, **body.model_dump(exclude_unset=True)
    )
    if user is None:
        raise NotFoundError("User not found.")
    return UserRead.model_validate(user)


@router.delete(
    "/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user"
)
async def delete_user(
    user_id: uuid.UUID, repo: UserRepository = Depends(get_user_repository)
) -> Response:
    if not await repo.delete(user_id):
        raise NotFoundError("User not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
