"""
LLM Prompt Cache for Jarvis X / Alfred OS.

A lightweight, thread-safe, in-memory LRU cache designed for caching
LLM prompt responses to reduce API latency and costs.
"""

import functools
import hashlib
import json
import threading
from typing import Any, Callable, Hashable, Optional

class LRUCache:
    """
    A thread-safe Least Recently Used (LRU) cache.
    """

    def __init__(self, maxsize: int = 128):
        """
        Initialize the LRU cache.

        Args:
            maxsize: Maximum number of items to store before evicting the oldest.
        """
        self.maxsize = maxsize
        self._cache: dict[Hashable, Any] = {}
        self._lock = threading.Lock()

    def get(self, key: Hashable) -> Optional[Any]:
        """
        Retrieve an item from the cache.

        Args:
            key: The cache key.

        Returns:
            The cached value if found, None otherwise.
        """
        with self._lock:
            if key not in self._cache:
                return None
            # Move to end to mark as most recently used
            value = self._cache.pop(key)
            self._cache[key] = value
            return value

    def set(self, key: Hashable, value: Any) -> None:
        """
        Store an item in the cache.

        Args:
            key: The cache key.
            value: The value to cache.
        """
        with self._lock:
            if key in self._cache:
                # Remove to re-insert at end (move to most recently used)
                self._cache.pop(key)
            elif len(self._cache) >= self.maxsize:
                # Evict least recently used item (first item in dict)
                self._cache.pop(next(iter(self._cache)))
            
            self._cache[key] = value

    def clear(self) -> None:
        """Clear all items from the cache."""
        with self._lock:
            self._cache.clear()

    def __len__(self) -> int:
        """Return the number of items currently in the cache."""
        with self._lock:
            return len(self._cache)


def _generate_cache_key(args: tuple, kwargs: dict) -> str:
    """
    Generate a deterministic cache key from function arguments.
    
    We use a SHA-256 hash of the JSON-serialized arguments to ensure
    uniqueness and a fixed-size key.
    """
    try:
        # Sort kwargs keys for consistency
        args_repr = repr(args)
        kwargs_repr = repr(sorted(kwargs.items()))
        key_string = f"{args_repr}:{kwargs_repr}"
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()
    except Exception:
        # Fallback if arguments are not serializable/repr-able
        return str(id(args)) + str(id(kwargs))


def llm_prompt_cache(maxsize: int = 128) -> Callable:
    """
    Decorator to cache LLM prompt results.
    
    Args:
        maxsize: Maximum number of unique prompts to cache.
        
    Returns:
        A decorator function.
    """
    cache = LRUCache(maxsize=maxsize)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = _generate_cache_key(args, kwargs)
            
            # Check cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache (only if result is not None, to allow retrying failed calls)
            if result is not None:
                cache.set(key, result)
                
            return result
        
        # Expose cache management methods for Jarvis X introspection
        wrapper.cache_clear = cache.clear
        wrapper.cache_info = lambda: {"size": len(cache), "maxsize": maxsize}
        
        return wrapper
    return decorator