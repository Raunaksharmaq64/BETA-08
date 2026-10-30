"""
RIGHT FIT Core — Rate Limiting & Abuse Prevention Service
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation

Implements sliding-window rate limiting with in-memory fallback for local dev/testing
and distributed Redis integration when available.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, List, Tuple


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter."""

    def __init__(self) -> None:
        self._store: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
        """Checks if a request under `key` is allowed.
        Returns:
            (allowed: bool, retry_after_seconds: int)
        """
        now = time.time()
        window_start = now - window_seconds
        timestamps = self._store[key]

        # Prune timestamps outside current window
        valid_timestamps = [ts for ts in timestamps if ts > window_start]
        self._store[key] = valid_timestamps

        if len(valid_timestamps) >= max_requests:
            earliest_timestamp = valid_timestamps[0]
            retry_after = max(1, int(window_seconds - (now - earliest_timestamp)))
            return False, retry_after

        self._store[key].append(now)
        return True, 0

    def reset(self, key: Optional[str] = None) -> None:
        """Resets rate limit counter for a specific key or all keys."""
        if key:
            self._store.pop(key, None)
        else:
            self._store.clear()


# Global rate limiter instance
rate_limiter = SlidingWindowRateLimiter()
