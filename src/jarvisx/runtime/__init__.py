from __future__ import annotations
from typing import Any

__all__ = [
    "JarvisRuntime",
    "create_default_runtime",
    "RuntimeState",
    "BootstrapManager",
    "ShutdownManager",
]

def __getattr__(name: str) -> Any:
    if name in ("JarvisRuntime", "create_default_runtime"):
        from jarvisx.runtime.runtime import JarvisRuntime, create_default_runtime
        return JarvisRuntime if name == "JarvisRuntime" else create_default_runtime
    elif name == "RuntimeState":
        from jarvisx.runtime.state import RuntimeState
        return RuntimeState
    elif name == "BootstrapManager":
        from jarvisx.runtime.bootstrap import BootstrapManager
        return BootstrapManager
    elif name == "ShutdownManager":
        from jarvisx.runtime.shutdown import ShutdownManager
        return ShutdownManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
