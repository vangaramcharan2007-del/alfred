from __future__ import annotations

from typing import Any
from jarvisx.core.capabilities.base import Capability, CapabilityProvider, ProviderError
from jarvisx.core.capabilities.evaluation import ProviderEvaluation
from jarvisx.core.os_control.app_launcher import AppLauncher


class DesktopProvider(CapabilityProvider):
    name = "SystemDesktop"
    capability = Capability.DESKTOP

    def is_available(self) -> bool:
        return True

    def evaluate(self, task: dict[str, Any]) -> ProviderEvaluation:
        return ProviderEvaluation(
            provider_name=self.name,
            capability=self.capability.name,
            score=90.0,
            available=True,
            confidence=0.9,
            latency_ms=10.0,
            reason="Native OS execution layer."
        )

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Executes a desktop action.
        task shape: {"action": "open" | "close", "target": "app_name"}
        """
        action = task.get("action")
        target = task.get("target")

        if not action or not target:
            raise ProviderError("Desktop task requires 'action' and 'target'.")

        # Note: We migrate the AppLauncher's logic here securely behind the Provider.
        # This prevents Alfred from manually resolving "open VS Code" to AppLauncher.
        if action == "open":
            success = AppLauncher.launch(target)
            if not success:
                raise ProviderError(f"Failed to open desktop application: {target}")
            return {"status": "success", "message": f"Successfully opened {target}."}
        
        elif action == "close":
            success = AppLauncher.close(target)
            if not success:
                raise ProviderError(f"Failed to close desktop application: {target}")
            return {"status": "success", "message": f"Successfully closed {target}."}
            
        else:
            raise ProviderError(f"Unsupported desktop action: {action}")
