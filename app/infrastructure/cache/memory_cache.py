"""In-memory cache backend.

A process-local `CacheService` used for tests and local runs without Redis.
Not shared across processes and not evicted by size — suitable only for dev.
"""

from __future__ import annotations

import time

from app.domain.interfaces.cache import CacheService


class InMemoryCacheService(CacheService):
    """Dict-backed cache with monotonic-clock expiry."""

    def __init__(self) -> None:
        # key -> (expires_at_monotonic | None, value)
        self._store: dict[str, tuple[float | None, str]] = {}

    async def get(self, key: str) -> str | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if expires_at is not None and time.monotonic() >= expires_at:
            self._store.pop(key, None)  # lazy expiry
            return None
        return value

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        expires_at = time.monotonic() + ttl if ttl else None
        self._store[key] = (expires_at, value)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def incr(self, key: str, ttl: int | None = None) -> int:
        now = time.monotonic()
        entry = self._store.get(key)
        # Start a fresh window if absent or the current window expired.
        if entry is None or (entry[0] is not None and now >= entry[0]):
            expires_at = now + ttl if ttl else None
            self._store[key] = (expires_at, "1")
            return 1
        count = int(entry[1]) + 1
        self._store[key] = (entry[0], str(count))  # keep original window expiry
        return count
