"""High-performance low-overhead memory pool engine with automatic GC and caching."""

import math
import threading
import time
import weakref
from typing import Dict, Optional, Tuple


class MemoryBlock:
    """Wrapper around a pre-allocated bytearray memory slice."""

    __slots__ = ("_view", "_pool", "_raw", "_active", "_finalizer")

    def __init__(self, pool: "SizeClassPool", raw_buffer: bytearray, size: int):
        self._pool = pool
        self._raw = raw_buffer
        self._view = memoryview(raw_buffer)[:size]
        self._active = True
        self._finalizer = weakref.finalize(self, pool.recycle, raw_buffer)

    @property
    def view(self) -> memoryview:
        if not self._active:
            raise RuntimeError("Attempted to access released MemoryBlock")
        return self._view

    def release(self) -> None:
        if self._active:
            self._active = False
            if self._finalizer.detach():
                self._pool.recycle(self._raw)

    def __enter__(self) -> memoryview:
        return self.view

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()


class SizeClassPool:
    """Manages allocation and caching for a specific size class."""

    __slots__ = (
        "size",
        "max_capacity",
        "_free_stack",
        "_lock",
        "allocated_count",
        "last_accessed",
    )

    def __init__(self, size: int, max_capacity: int = 1024):
        self.size = size
        self.max_capacity = max_capacity
        self._free_stack = []
        self._lock = threading.Lock()
        self.allocated_count = 0
        self.last_accessed = time.monotonic()

    def acquire() -> bytearray:
        self.last_accessed = time.monotonic()
        with self._lock:
            if self._free_stack:
                return self._free_stack.pop()
            self.allocated_count += 1
        return bytearray(self.size)

    def recycle(self, raw_buffer: bytearray) -> None:
        self.last_accessed = time.monotonic()
        with self._lock:
            if len(self._free_stack) < self.max_capacity:
                self._free_stack.append(raw_buffer)
            else:
                self.allocated_count -= 1

    def purge(self, keep_ratio: float = 0.25) -> int:
        with self._lock:
            target_size = int(len(self._free_stack) * keep_ratio)
            evicted = len(self._free_stack) - target_size
            if evicted > 0:
                del self._free_stack[target_size:]
                self.allocated_count -= evicted
                return evicted
            return 0


class MemoryEngine:
    """Thread-safe memory engine providing pooled allocations, caching, and GC."""

    def __init__(
        self,
        min_block_size: int = 64,
        max_block_size: int = 1048576,
        max_cached_per_class: int = 1024,
        gc_ttl_seconds: float = 30.0,
    ):
        self._min_block_size = min_block_size
        self._max_block_size = max_block_size
        self._max_cached = max_cached_per_class
        self._gc_ttl = gc_ttl_seconds
        self._pools: Dict[int, SizeClassPool] = {}
        self._lock = threading.Lock()
        self._last_gc = time.monotonic()

    def _size_to_class(self, size: int) -> int:
        if size <= self._min_block_size:
            return self._min_block_size
        return 1 << (size - 1).bit_length()

    def _get_pool(self, size_class: int) -> SizeClassPool:
        pool = self._pools.get(size_class)
        if pool is None:
            with self._lock:
                pool = self._pools.get(size_class)
                if pool is None:
                    pool = SizeClassPool(size_class, self._max_cached)
                    self._pools[size_class] = pool
        return pool

    def allocate(self, size: int) -> MemoryBlock:
        if size <= 0:
            raise ValueError("Allocation size must be positive")
        if size > self._max_block_size:
            raise ValueError(f"Allocation size exceeds maximum limit of {self._max_block_size} bytes")

        self.maybe_collect()
        size_class = self._size_to_class(size)
        pool = self._get_pool(size_class)
        raw_buf = pool.acquire()
        return MemoryBlock(pool, raw_buf, size)

    def maybe_collect(self, force: bool = False) -> int:
        now = time.monotonic()
        if not force and (now - self._last_gc < self._gc_ttl):
            return 0

        self._last_gc = now
        total_evicted = 0
        for pool in list(self._pools.values()):
            if force or (now - pool.last_accessed > self._gc_ttl):
                total_evicted += pool.purge(keep_ratio=0.0 if force else 0.25)
        return total_evicted

    def stats(self) -> Dict[str, Dict[str, int]]:
        stats_map = {}
        with self._lock:
            for size_class, pool in self._pools.items():
                stats_map[f"{size_class}B"] = {
                    "allocated": pool.allocated_count,
                    "cached": len(pool._free_stack),
                    "active": pool.allocated_count - len(pool._free_stack),
                }
        return stats_map

    def clear(self) -> None:
        with self._lock:
            for pool in self._pools.values():
                pool.purge(keep_ratio=0.0)
            self._pools.clear()
