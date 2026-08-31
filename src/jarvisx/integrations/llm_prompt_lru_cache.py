"""
Jarvis X / Alfred OS - Prompt Cache Module
Zero-dependency, thread-safe LRU cache with TTL expiry for LLM prompt deduplication.
"""

from collections import OrderedDict
from dataclasses import dataclass
import functools
import inspect
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, Union
import threading
import time

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(slots=True)
class CacheEntry:
    value: Any
    expires_at: float


@dataclass(slots=True)
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    current_size: int = 0
    maxsize: int = 0


class TTLLRUCache:
    """Thread-safe LRU Cache with Time-To-Live (TTL) expiration."""

    def __init__(self, maxsize: int = 1024, ttl: float = 300.0) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be greater than 0")
        if ttl <= 0:
            raise ValueError("ttl must be greater than 0")

        self.maxsize: int = maxsize
        self.ttl: float = ttl
        self._cache: OrderedDict[HashableKey, CacheEntry] = OrderedDict()
        self._lock: threading.RLock = threading.RLock()

        self._hits: int = 0
        self._misses: int = 0
        self._evictions: int = 0
        self._expirations: int = 0

    def _generate_key(self, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> HashableKey:
        """Constructs a deterministic, hashable key from function arguments."""
        key_items: list[Any] = []
        for arg in args:
            key_items.append(self._make_hashable(arg))

        for k, v in sorted(kwargs.items()):
            key_items.append((k, self._make_hashable(v)))

        return tuple(key_items)

    def _make_hashable(self, val: Any) -> Any:
        """Recursively converts unhashable types to hashable equivalents."""
        if isinstance(val, (int, float, str, bool, type(None), bytes)):
            return val
        elif isinstance(val, (tuple, list)):
            return tuple(self._make_hashable(item) for item in val)
        elif isinstance(val, dict):
            return tuple(sorted((k, self._make_hashable(v)) for k, v in val.items()))
        elif isinstance(val, set):
            return tuple(sorted(self._make_hashable(item) for item in val))
        else:
            return str(val)

    def get(self, key: HashableKey) -> Optional[Any]:
        """Retrieves a value from cache if present and not expired."""
        now = time.monotonic()
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]

            if now >= entry.expires_at:
                del self._cache[key]
                self._expirations += 1
                self._misses += 1
                return None

            self._cache.move_to_end(key)
            self._hits += 1
            return entry.value

    def put(self, key: HashableKey, value: Any) -> None:
        """Stores a value in cache, enforcing TTL and LRU maxsize constraints."""
        now = time.monotonic()
        expires_at = now + self.ttl

        with self._lock:
            if key in self._cache:
                self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
                self._cache.move_to_end(key)
                return

            if len(self._cache) >= self.maxsize:
                self._cache.popitem(last=False)
                self._evictions += 1

            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    def clear(self) -> None:
        """Flushes all cached entries and resets operational counters."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
            self._expirations = 0

    def stats(self) -> CacheStats:
        """Returns snapshot telemetry of the cache performance."""
        with self._lock:
            return CacheStats(
                hits=self._hits,
                misses=self._misses,
                evictions=self._evictions,
                expirations=self._expirations,
                current_size=len(self._cache),
                maxsize=self.maxsize,
            )


HashableKey = Tuple[Any, ...]


def ttl_lru_cache(maxsize: int = 1024, ttl: float = 300.0) -> Callable[[F], F]:
    """
    Decorator for caching LLM prompts/responses with TTL expiry and LRU eviction.
    Supports both synchronous and asynchronous functions.
    """
    cache = TTLLRUCache(maxsize=maxsize, ttl=ttl)

    def decorator(fn: F) -> F:
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                key = cache._generate_key(args, kwargs)
                cached_res = cache.get(key)
                if cached_res is not None:
                    return cached_res

                result = await fn(*args, **kwargs)
                cache.put(key, result)
                return result

            async_wrapper.cache = cache  # type: ignore[attr-defined]
            return async_wrapper  # type: ignore[return-value]
        else:
            @functools.wraps(fn)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                key = cache._generate_key(args, kwargs)
                cached_res = cache.get(key)
                if cached_res is not None:
                    return cached_res

                result = fn(*args, **kwargs)
                cache.put(key, result)
                return result

            sync_wrapper.cache = cache  # type: ignore[attr-defined]
            return sync_wrapper  # type: ignore[return-value]

    return decorator