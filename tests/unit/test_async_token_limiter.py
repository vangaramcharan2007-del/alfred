import asyncio
import time
import pytest

from rate_limiter import TokenBucket


@pytest.mark.asyncio
async def test_initial_state_full():
    """Test that the bucket starts full."""
    bucket = TokenBucket(capacity=10, refill_rate=1.0)
    assert bucket.available_tokens == 10.0


@pytest.mark.asyncio
async def test_acquire_decreases_tokens():
    """Test that acquiring tokens decreases the available count."""
    bucket = TokenBucket(capacity=10, refill_rate=1.0)
    await bucket.acquire(3.0)
    # Allow a tiny bit of time for precise assertion if needed, 
    # but since we just refilled in __post_init__, it should be close to 7.
    assert 6.9 < bucket.available_tokens <= 7.0


@pytest.mark.asyncio
async def test_acquire_blocks_until_refill():
    """Test that acquire waits if tokens are insufficient."""
    bucket = TokenBucket(capacity=2, refill_rate=100.0)  # Fast refill for test speed
    
    # Consume all tokens
    await bucket.acquire(2.0)
    
    # Next acquire should block briefly
    start_time = time.monotonic()
    await bucket.acquire(1.0)
    end_time = time.monotonic()
    
    elapsed = end_time - start_time
    # Should have waited at least a small amount of time for 1 token
    # At 100 tokens/sec, 1 token takes 0.01s. Allow some margin.
    assert elapsed >= 0.005


@pytest.mark.asyncio
async def test_try_acquire_non_blocking():
    """Test that try_acquire returns False immediately if tokens are low."""
    bucket = TokenBucket(capacity=1, refill_rate=0.1)  # Slow refill
    
    assert await bucket.try_acquire(1.0) is True
    # Since refill is slow, the next try_acquire should fail immediately
    assert await bucket.try_acquire(1.0) is False


@pytest.mark.asyncio
async def test_capacity_exceeded_raises():
    """Test that requesting more than capacity raises ValueError."""
    bucket = TokenBucket(capacity=5, refill_rate=1.0)
    with pytest.raises(ValueError):
        await bucket.acquire(6.0)


@pytest.mark.asyncio
async def test_concurrent_access_safety():
    """Test that concurrent access does not corrupt state."""
    bucket = TokenBucket(capacity=10, refill_rate=1000.0)  # Fast refill to avoid long waits
    
    async def consume():
        for _ in range(5):
            await bucket.acquire(1.0)
    
    # Run multiple consumers concurrently
    await asyncio.gather(*[consume() for _ in range(5)])
    
    # Total 25 tokens consumed, capacity 10, high refill rate.
    # The bucket should have refilled enough to handle the load, 
    # or be in a valid state (tokens between 0 and 10).
    assert 0.0 <= bucket.available_tokens <= 10.0