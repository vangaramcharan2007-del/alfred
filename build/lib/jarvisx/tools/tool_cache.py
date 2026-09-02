"""
Tool Result Cache — Lightweight TTL-Based In-Memory Cache for Idempotent Tools.
Eliminates redundant re-execution of read-only tools like get_system_info,
get_current_time, read_file, list_directory, web_search.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger("jarvisx.tools.tool_cache")


# TTL in seconds per tool. Only tools listed here are cached.
CACHEABLE_TOOLS: Dict[str, int] = {
    "get_system_info": 30,
    "get_current_time": 5,
    "list_directory": 15,
    "read_file": 60,
    "get_active_window": 3,
    "list_windows": 5,
    "web_search": 300,
    "fetch_webpage": 300,
}


class ToolResultCache:
    """Simple in-memory TTL cache for idempotent tool results."""

    _instance: Optional["ToolResultCache"] = None

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}
        self._hits = 0
        self._misses = 0

    @classmethod
    def get_instance(cls) -> "ToolResultCache":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def _cache_key(tool_name: str, arguments: Dict[str, Any]) -> str:
        """Deterministic cache key from tool name + sorted arguments."""
        args_str = json.dumps(arguments, sort_keys=True, default=str)
        raw = f"{tool_name}:{args_str}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """Returns cached result if available and not expired, else None."""
        ttl = CACHEABLE_TOOLS.get(tool_name)
        if ttl is None:
            return None  # Not a cacheable tool

        key = self._cache_key(tool_name, arguments)
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            return None

        age = time.time() - entry["timestamp"]
        if age > ttl:
            del self._store[key]
            self._misses += 1
            return None

        self._hits += 1
        logger.debug(f"[ToolCache] HIT for {tool_name} (age={age:.1f}s, ttl={ttl}s)")
        return entry["result"]

    def put(self, tool_name: str, arguments: Dict[str, Any], result: Any) -> None:
        """Store a tool result in the cache."""
        if tool_name not in CACHEABLE_TOOLS:
            return
        key = self._cache_key(tool_name, arguments)
        self._store[key] = {
            "tool": tool_name,
            "timestamp": time.time(),
            "result": result,
        }

    def invalidate(self, tool_name: Optional[str] = None) -> None:
        """Invalidate cache entries. If tool_name is None, flush entire cache."""
        if tool_name is None:
            self._store.clear()
        else:
            to_del = [k for k, v in self._store.items() if v.get("tool") == tool_name]
            for k in to_del:
                del self._store[k]

    def stats(self) -> Dict[str, Any]:
        return {
            "entries": len(self._store),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / max(self._hits + self._misses, 1) * 100, 1),
        }
