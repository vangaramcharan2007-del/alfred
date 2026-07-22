from __future__ import annotations

from enum import Enum, auto
from typing import Any, Optional
from abc import abstractmethod

from jarvisx.core.capabilities.evaluation import ProviderEvaluation, ProviderHealth


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

    def __init__(self):
        self._health = ProviderHealth()
        
    @property
    def health(self) -> ProviderHealth:
        return self._health

    def is_available(self) -> bool:
        """Check if this provider is installed and ready to be used."""
        return True

    @abstractmethod
    def evaluate(self, task: dict[str, Any]) -> ProviderEvaluation:
        """
        Evaluates how well this provider can handle the given task.
        """
        # Default implementation (should be overridden)
        return ProviderEvaluation(
            provider_name=self.name,
            capability=self.capability.name,
            score=50.0 if self.is_available() else 0.0,
            available=self.is_available(),
            confidence=0.5,
            reason="Default base evaluation"
        )

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a capability task.
        Returns a dictionary containing the result or raises ProviderError.
        """
        raise NotImplementedError("Providers must implement execute()")

    def verify(self, task: dict[str, Any]) -> bool:
        """
        Verifies if the execution was successful (e.g. process is running, file created).
        Returns True if successful or un-verifiable, False if verification fails.
        """
        return True
