from __future__ import annotations
from typing import Any
import webbrowser
from jarvisx.core.capabilities.base import Capability, CapabilityProvider, ProviderError
from jarvisx.core.capabilities.evaluation import ProviderEvaluation

class BraveProvider(CapabilityProvider):
    name = "Brave"
    capability = Capability.BROWSER

    def is_available(self) -> bool:
        return True

    def evaluate(self, task: dict[str, Any]) -> ProviderEvaluation:
        available = self.is_available()
        return ProviderEvaluation(
            provider_name=self.name,
            capability=self.capability.name,
            score=99.0 if available else 0.0,
            available=available,
            confidence=1.0 if available else 0.0,
            latency_ms=20.0,
            reason="Brand new fast provider."
        )

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        return {"status": "success", "message": "Executed via Brave!"}
