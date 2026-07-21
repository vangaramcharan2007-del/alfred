from __future__ import annotations

from enum import Enum, auto
from typing import Any, Optional


class Capability(Enum):
    """
    Core capabilities of the Jarvis X operating system.
    Alfred thinks in these terms, never in terms of specific applications.
    """
    BROWSER = auto()
    COMMUNICATION = auto()
    DESKTOP = auto()
    FILE_SYSTEM = auto()
    MEDIA = auto()
    VISION = auto()
    PLANNING = auto()
    MEMORY = auto()
    KNOWLEDGE = auto()


class ProviderError(Exception):
    """Raised when a provider fails to execute a task."""
    pass


class CapabilityProvider:
    """
    Abstract base class for all capability providers (plugins).
    A provider implements exactly one capability (e.g. Chrome implements BROWSER).
    """
    name: str = "BaseProvider"
    capability: Capability = Capability.BROWSER

    def is_available(self) -> bool:
        """Check if this provider is installed and ready to be used."""
        return True

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a capability task.
        Returns a dictionary containing the result or raises ProviderError.
        """
        raise NotImplementedError("Providers must implement execute()")
