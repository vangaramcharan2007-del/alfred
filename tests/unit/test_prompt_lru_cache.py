import pytest
import time
from llm_prompt_cache import llm_prompt_cache, LRUCache

class TestLRUCache:
    def test_basic_set_get(self):
        cache = LRUCache(maxsize=2)
        cache.set("a", 1)
        assert cache.get("a") == 1
        assert cache.get("b") is None

    def test_lru_eviction(self):
        cache = LRUCache(maxsize=2)
        cache.set("a", 1)
        cache.set("b", 2)
        
        # Access 'a' to make it most recently used
        cache.get("a")
        
        # Add 'c', should evict 'b' (least recently used)
        cache.set("c", 3)
        
        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3

    def test_thread_safety(self):
        cache = LRUCache(maxsize=100)
        import threading
        
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(100):
                    key = f"key_{thread_id}_{i}"
                    cache.set(key, i)
                    cache.get(key)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        assert not errors

@llm_prompt_cache(maxsize=10)
def mock_llm_call(prompt: str) -> str:
    """Simulate an LLM API call."""
    # Simulate network delay
    time.sleep(0.01)
    return f"Response to: {prompt}"

def test_llm_prompt_cache_decorator():
    # First call should be slow (no cache)
    start = time.time()
    result1 = mock_llm_call("Hello")
    time1 = time.time() - start
    
    # Second call should be fast (cached)
    start = time.time()
    result2 = mock_llm_call("Hello")
    time2 = time.time() - start
    
    assert result1 == result2 == "Response to: Hello"
    assert time2 < time1  # Cached version should be faster
    
    # Different prompt should not be cached
    result3 = mock_llm_call("World")
    assert result3 == "Response to: World"
    
    # Check cache info
    info = mock_llm_call.cache_info()
    assert info["size"] == 2
    assert info["maxsize"] == 10

def test_llm_prompt_cache_clear():
    mock_llm_call("Test")
    mock_llm_call.cache_clear()
    assert mock_llm_call.cache_info()["size"] == 0

def test_llm_prompt_cache_none_result_not_cached():
    @llm_prompt_cache(maxsize=10)
    def flaky_llm(prompt: str) -> str:
        return None  # Simulate a failed/empty response
    
    flaky_llm("Test")
    # None results should not be cached, so cache size remains 0
    assert flaky_llm.cache_info()["size"] == 0