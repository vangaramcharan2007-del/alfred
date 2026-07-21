from __future__ import annotations

from typing import Any

from jarvisx.core.capabilities.base import Capability, CapabilityProvider, ProviderError
from jarvisx.core.capabilities.evaluation import ProviderEvaluation
# Re-use the existing logic under the hood without Alfred importing it directly
from jarvisx.core.whatsapp.manager import WhatsAppAutomationManager


class WhatsAppProvider(CapabilityProvider):
    name = "WhatsApp"
    capability = Capability.COMMUNICATION

    def __init__(self):
        self._manager = None
        
    def is_available(self) -> bool:
        # Check if the UI controller can run (e.g. Windows environment with pywinauto)
        try:
            import pywinauto
            return True
        except ImportError:
            return False

    def evaluate(self, task: dict[str, Any]) -> ProviderEvaluation:
        available = self.is_available()
        return ProviderEvaluation(
            provider_name=self.name,
            capability=self.capability.name,
            score=95.0 if available else 0.0,
            available=available,
            confidence=0.9 if available else 0.0,
            latency_ms=100.0,
            reason="GUI automation is active." if available else "pywinauto not found."
        )

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Executes communication tasks.
        Supported task structures:
        {
            "action": "start_monitoring" | "pause_monitoring" | "resume_monitoring" | "get_stats"
        }
        """
        action = task.get("action")
        if not action:
            raise ProviderError("WhatsAppProvider requires an 'action' in the task definition.")
            
        if self._manager is None:
            # Lazy initialization
            self._manager = WhatsAppAutomationManager()

        if action == "start_monitoring":
            self._manager.start()
            return {"status": "started", "message": "I am now monitoring WhatsApp for incoming Word documents."}
            
        elif action == "pause_monitoring":
            self._manager.pause()
            return {"status": "paused", "message": "WhatsApp monitoring paused."}
            
        elif action == "resume_monitoring":
            self._manager.resume()
            return {"status": "resumed", "message": "WhatsApp monitoring resumed."}
            
        elif action == "get_stats":
            count = self._manager.files_converted_today
            return {"status": "success", "count": count, "message": f"I have converted {count} documents from WhatsApp today."}
            
        else:
            raise ProviderError(f"Unsupported WhatsAppProvider action: {action}")
