"""
Unit Tests: Sliding Window Rate Limiter
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

import time
from app.services.rate_limiter import SlidingWindowRateLimiter


def test_sliding_window_rate_limiter():
    limiter = SlidingWindowRateLimiter()
    key = "test_ip_192.168.1.1"

    # Allow up to 3 requests in 10-second window
    assert limiter.is_allowed(key, max_requests=3, window_seconds=10)[0] is True
    assert limiter.is_allowed(key, max_requests=3, window_seconds=10)[0] is True
    assert limiter.is_allowed(key, max_requests=3, window_seconds=10)[0] is True

    # 4th request must be blocked
    allowed, retry_after = limiter.is_allowed(key, max_requests=3, window_seconds=10)
    assert allowed is False
    assert retry_after > 0


def test_rate_limiter_reset():
    limiter = SlidingWindowRateLimiter()
    key = "user_reset_test"
    limiter.is_allowed(key, max_requests=1, window_seconds=60)
    assert limiter.is_allowed(key, max_requests=1, window_seconds=60)[0] is False

    limiter.reset(key)
    assert limiter.is_allowed(key, max_requests=1, window_seconds=60)[0] is True
