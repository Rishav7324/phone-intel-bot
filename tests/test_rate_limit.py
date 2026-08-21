"""Unit tests for sliding window rate limiting."""

import asyncio
import pytest
from bot.utils.rate_limit import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_allows_under_threshold():
    """Verify that requests within quota are allowed."""
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    user_id = 12345

    for _ in range(5):
        allowed, retry_after = await limiter.is_allowed(user_id)
        assert allowed is True
        assert retry_after == 0


@pytest.mark.asyncio
async def test_rate_limiter_blocks_over_threshold():
    """Verify that requests exceeding quota are blocked with retry time."""
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    user_id = 99999

    for _ in range(3):
        allowed, _ = await limiter.is_allowed(user_id)
        assert allowed is True

    # 4th request must be blocked
    allowed, retry_after = await limiter.is_allowed(user_id)
    assert allowed is False
    assert retry_after > 0
    assert retry_after <= 60


@pytest.mark.asyncio
async def test_rate_limiter_distinct_users():
    """Verify that one user's quota does not impact another user."""
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    user_a = 1001
    user_b = 1002

    # Exhaust user_a
    await limiter.is_allowed(user_a)
    await limiter.is_allowed(user_a)
    allowed_a, _ = await limiter.is_allowed(user_a)
    assert allowed_a is False

    # User B should still be allowed
    allowed_b, _ = await limiter.is_allowed(user_b)
    assert allowed_b is True


@pytest.mark.asyncio
async def test_rate_limiter_reset_user():
    """Verify manual reset of a user's rate limits."""
    limiter = RateLimiter(max_requests=1, window_seconds=60)
    user_id = 55555

    await limiter.is_allowed(user_id)
    allowed, _ = await limiter.is_allowed(user_id)
    assert allowed is False

    limiter.reset_user(user_id)
    allowed_after_reset, _ = await limiter.is_allowed(user_id)
    assert allowed_after_reset is True
