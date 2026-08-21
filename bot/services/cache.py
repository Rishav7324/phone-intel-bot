"""Thread-safe in-memory cache with Time-To-Live (TTL) expiration."""

import asyncio
import time
from typing import Any, Dict, Optional, Tuple


class MemoryCache:
    """Asynchronous in-memory key-value cache with TTL expiration."""

    def __init__(self, default_ttl: int = 600, max_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._store: Dict[str, Tuple[Any, float]] = {}  # key -> (value, expire_timestamp)
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached value if not expired."""
        async with self._lock:
            if key not in self._store:
                return None
            value, expires_at = self._store[key]
            if time.time() > expires_at:
                del self._store[key]
                return None
            return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a key-value pair with expiration time."""
        effective_ttl = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + effective_ttl

        async with self._lock:
            # Enforce max cache size by purging expired or oldest items
            if len(self._store) >= self.max_size:
                self._evict_expired()
                if len(self._store) >= self.max_size:
                    # Remove oldest inserted item
                    oldest_key = next(iter(self._store))
                    del self._store[oldest_key]

            self._store[key] = (value, expires_at)

    def _evict_expired(self) -> None:
        """Evict expired items from cache."""
        now = time.time()
        expired_keys = [k for k, (_, exp) in self._store.items() if now > exp]
        for k in expired_keys:
            del self._store[k]

    async def delete(self, key: str) -> None:
        """Delete an item from cache."""
        async with self._lock:
            if key in self._store:
                del self._store[key]

    async def clear(self) -> None:
        """Clear all cached entries."""
        async with self._lock:
            self._store.clear()
