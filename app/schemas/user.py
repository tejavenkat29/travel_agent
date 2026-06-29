"""User API schemas (request/response DTOs for the CRUD endpoints)."""

from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Unique email address")
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # Allow building this from an ORM object (orm_mode in Pydantic v2).
    model_config = {"from_attributes": True}
