"""Cache service port (interface).

A minimal, backend-agnostic key/value cache contract with TTL. The application
depends on this abstraction; Redis and in-memory implementations live in the
infrastructure layer (Dependency Inversion). Values are opaque strings —
callers serialize/deserialize their own domain objects.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class CacheService(ABC):
    """Key/value cache with per-entry expiration."""

    @abstractmethod
    async def get(self, key: str) -> str | None:
        """Return the cached value, or None on miss/expiry."""

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Store a value with an optional time-to-live (seconds)."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove a key (no-op if absent)."""

    @abstractmethod
    async def incr(self, key: str, ttl: int | None = None) -> int:
        """Atomically increment a counter; set ttl only on first increment.

        Used for fixed-window rate limiting. Returns the new count.
        """
