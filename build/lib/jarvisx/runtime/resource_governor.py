"""Resource Governor & Lazy-Loading Manager for Phase 104.5."""

from __future__ import annotations
import logging
import threading
import time
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("jarvisx.resource_governor")


class ResourceGovernor:
    """Manages lazy-loading of heavy AI models and unloads idle components to keep RAM < 120MB."""

    def __init__(self, max_idle_seconds: float = 900.0):  # 15 minutes default
        self.max_idle_seconds = max_idle_seconds
        self._components: Dict[str, Any] = {}
        self._loaders: Dict[str, Callable[[], Any]] = {}
        self._last_accessed: Dict[str, float] = {}
        self._lock = threading.Lock()

    def register_lazy_component(self, name: str, loader: Callable[[], Any]):
        """Register a heavy component loader without executing it at boot."""
        with self._lock:
            self._loaders[name] = loader

    def get_component(self, name: str) -> Optional[Any]:
        """Fetch component, loading on-demand if not already loaded into RAM."""
        with self._lock:
            self._last_accessed[name] = time.time()
            if name in self._components:
                return self._components[name]

            loader = self._loaders.get(name)
            if not loader:
                return None

            logger.info(f"[ResourceGovernor] Lazy-loading heavy component: '{name}' on-demand...")
            try:
                comp = loader()
                self._components[name] = comp
                return comp
            except Exception as e:
                logger.error(f"[ResourceGovernor] Failed to lazy-load '{name}': {e}")
                return None

    def is_loaded(self, name: str) -> bool:
        with self._lock:
            return name in self._components

    def unload_component(self, name: str) -> bool:
        """Explicitly unload a heavy component from RAM."""
        with self._lock:
            if name in self._components:
                del self._components[name]
                logger.info(f"[ResourceGovernor] Unloaded component '{name}' to conserve RAM.")
                return True
            return False

    def evict_idle_components(self) -> int:
        """Evict components that have exceeded the idle threshold."""
        now = time.time()
        evicted = 0
        with self._lock:
            to_evict = [
                name
                for name, last_acc in self._last_accessed.items()
                if name in self._components and (now - last_acc) > self.max_idle_seconds
            ]
            for name in to_evict:
                del self._components[name]
                evicted += 1
                logger.info(f"[ResourceGovernor] Idle eviction: '{name}' unloaded from RAM.")
        return evicted

    def get_loaded_status(self) -> Dict[str, bool]:
        """Return memory status of all registered components."""
        with self._lock:
            return {
                name: (name in self._components)
                for name in self._loaders.keys()
            }
