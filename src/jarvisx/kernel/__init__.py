"""Kernel Layer Exports for Jarvis X (Layer 2 - Alfred Intelligence Layer)."""

from __future__ import annotations

from typing import Any

__all__ = [
    "RuntimeKernel",
    "PersonalOSKernel",
    "AlfredDaemon",
]


def __getattr__(name: str) -> Any:
    if name == "RuntimeKernel":
        from jarvisx.kernel.runtime_kernel import RuntimeKernel
        return RuntimeKernel
    if name == "PersonalOSKernel":
        from jarvisx.kernel.personal_os import PersonalOSKernel
        return PersonalOSKernel
    if name == "AlfredDaemon":
        from jarvisx.kernel.daemon import AlfredDaemon
        return AlfredDaemon
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
