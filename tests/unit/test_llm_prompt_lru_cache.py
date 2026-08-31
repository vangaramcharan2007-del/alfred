import asyncio
import time
import pytest
from prompt_cache import ttl_lru_cache, TTLLRUCache


def test_cache_hit_and_miss():
    call_count = 0

    @ttl_lru_cache(maxsize=10, ttl=60.0)
    def generate_llm_response(prompt: str) -> str:
        nonlocal call_count
        call_count += 1
        return f"Response to: {prompt}"

    # First call: Cache Miss
    res1 = generate_llm_response("Hello Jarvis")
    assert res1 == "Response to: Hello Jarvis"
    assert call_count == 1

    # Second call: Cache Hit
    res2 = generate_llm_response("Hello Jarvis")
    assert res2 == "Response to: Hello Jarvis"
    assert call_count == 1  # Underlying function was not re-executed

    stats = generate_llm_response.cache.stats()
    assert stats.hits == 1
    assert stats.misses == 1
    assert stats.current_size == 1


def test_cache_ttl_expiration():
    call_count = 0

    @ttl_lru_cache(maxsize=10, ttl=0.1)  # 100ms TTL
    def quick_prompt(prompt: str) -> str:
        nonlocal call_count
        call_count += 1
        return f"Output: {prompt}"

    res1 = quick_prompt("System Status")
    assert res1 == "Output: System Status"
    assert call_count == 1

    # Sleep past expiration threshold
    time.sleep(0.15)

    res2 = quick_prompt("System Status")
    assert res2 == "Output: System Status"
    assert call_count == 2  # Re-executed due to TTL expiration

    stats = quick_prompt.cache.stats()
    assert stats.expirations == 1
    assert stats.misses == 2


def test_lru_eviction():
    cache = TTLLRUCache(maxsize=2, ttl=60.0)
    cache.put(("key1",), "val1")
    cache.put(("key2",), "val2")

    # Access key1 to make key2 the least recently used
    assert cache.get(("key1",)) == "val1"

    # Add key3, triggering eviction of key2
    cache.put(("key3",), "val3")

    assert cache.get(("key2",)) is None  # Evicted
    assert cache.get(("key1",)) == "val1"
    assert cache.get(("key3",)) == "val3"

    stats = cache.stats()
    assert stats.evictions == 1


@pytest.mark.asyncio
async def test_async_prompt_cache():
    call_count = 0

    @ttl_lru_cache(maxsize=5, ttl=10.0)
    async def async_llm_query(prompt: str, context: dict) -> str:
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.01)
        return f"Async response to {prompt}"

    res1 = await async_llm_query("Analyze logs", context={"depth": "high"})
    assert res1 == "Async response to Analyze logs"
    assert call_count == 1

    # Call with unhashable dict param (should be safely handled by hash generator)
    res2 = await async_llm_query("Analyze logs", context={"depth": "high"})
    assert res2 == "Async response to Analyze logs"
    assert call_count == 1

    stats = async_llm_query.cache.stats()
    assert stats.hits == 1
    assert stats.misses == 1