"""Async database engine, session factory, and the request session dependency.

Engine/sessionmaker are created lazily (and cached) so importing this module
never opens a connection — the app boots without a live database, and tests can
override `get_db` entirely.

`get_db` implements a per-request unit of work: it yields a session, commits on
success, and rolls back on any exception.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


@lru_cache
def get_engine():
    """Create (once) the async engine for the configured DATABASE_URL."""
    return create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Create (once) the async session factory."""
    return async_sessionmaker(
        bind=get_engine(), expire_on_commit=False, class_=AsyncSession
    )


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: a transactional session per request."""
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
