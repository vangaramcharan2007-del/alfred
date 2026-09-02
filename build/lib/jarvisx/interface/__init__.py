"""Lazy interface exports that keep the core runtime free of UI dependencies."""

from __future__ import annotations

from typing import Any

__all__ = [
    "JarvisCLI",
    "CommandParser",
    "VoiceRuntimeEngine",
    "MultiModalInterface",
]


def __getattr__(name: str) -> Any:
    if name == "JarvisCLI":
        from jarvisx.interface.cli import JarvisCLI
        return JarvisCLI
    if name == "CommandParser":
        from jarvisx.interface.command_parser import CommandParser
        return CommandParser
    if name == "VoiceRuntimeEngine":
        from jarvisx.interface.voice_runtime import VoiceRuntimeEngine
        return VoiceRuntimeEngine
    if name == "MultiModalInterface":
        from jarvisx.interface.multimodal import MultiModalInterface
        return MultiModalInterface
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
