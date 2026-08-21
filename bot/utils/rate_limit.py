"""Sliding window rate limiter for per-user and global request throttling."""

import asyncio
import time
from collections import defaultdict
from typing import Dict, List, Tuple


class RateLimiter:
    """In-memory sliding window rate limiter with auto-expiring user buckets."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._user_requests: Dict[int, List[float]] = defaultdict(list)
        self._global_requests: List[float] = []
        self._global_max: int = max_requests * 50  # Global protection headroom
        self._lock = asyncio.Lock()
        self._last_cleanup = time.time()

    async def is_allowed(self, user_id: int) -> Tuple[bool, int]:
        """Check if user is allowed to make a request.

        Returns:
            Tuple of (is_allowed: bool, retry_after_seconds: int)
        """
        async with self._lock:
            now = time.time()
            cutoff = now - self.window_seconds

            # Periodic cleanup of inactive users every 5 minutes
            if now - self._last_cleanup > 300:
                self._cleanup(cutoff)
                self._last_cleanup = now

            # Clean global requests
            self._global_requests = [ts for ts in self._global_requests if ts > cutoff]
            if len(self._global_requests) >= self._global_max:
                oldest = self._global_requests[0]
                retry_after = max(1, int(oldest + self.window_seconds - now))
                return False, retry_after

            # Clean user requests
            user_history = [ts for ts in self._user_requests[user_id] if ts > cutoff]
            self._user_requests[user_id] = user_history

            if len(user_history) >= self.max_requests:
                oldest = user_history[0]
                retry_after = max(1, int(oldest + self.window_seconds - now))
                return False, retry_after

            # Register current request
            self._user_requests[user_id].append(now)
            self._global_requests.append(now)
            return True, 0

    def _cleanup(self, cutoff: float) -> None:
        """Remove inactive user entries to free memory."""
        users_to_delete = []
        for uid, timestamps in self._user_requests.items():
            valid_ts = [ts for ts in timestamps if ts > cutoff]
            if not valid_ts:
                users_to_delete.append(uid)
            else:
                self._user_requests[uid] = valid_ts

        for uid in users_to_delete:
            del self._user_requests[uid]

    def reset_user(self, user_id: int) -> None:
        """Reset rate limit history for a specific user (e.g. testing or admin)."""
        if user_id in self._user_requests:
            del self._user_requests[user_id]

    def reset_all(self) -> None:
        """Clear all rate limit histories."""
        self._user_requests.clear()
        self._global_requests.clear()
