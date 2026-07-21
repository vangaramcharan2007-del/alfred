from __future__ import annotations

from typing import Any
import webbrowser
from jarvisx.core.capabilities.base import Capability, CapabilityProvider, ProviderError
from jarvisx.core.capabilities.evaluation import ProviderEvaluation


class FirefoxProvider(CapabilityProvider):
    name = "MozillaFirefox"
    capability = Capability.BROWSER

    def is_available(self) -> bool:
        return True

    def evaluate(self, task: dict[str, Any]) -> ProviderEvaluation:
        available = self.is_available()
        return ProviderEvaluation(
            provider_name=self.name,
            capability=self.capability.name,
            score=84.0 if available else 0.0,
            available=available,
            confidence=0.95 if available else 0.0,
            latency_ms=60.0,
            reason="Available but profile locked" if available else "Browser missing"
        )

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Executes a browser action using Firefox.
        """
        action = task.get("action")

        if action == "search":
            query = task.get("query")
            if not query:
                raise ProviderError("Browser search task requires 'query'.")
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open_new_tab(url)
            return {"status": "success", "message": f"Searched for '{query}' in Firefox."}
            
        elif action == "open_url":
            url = task.get("url")
            if not url:
                raise ProviderError("Browser open_url task requires 'url'.")
            webbrowser.open_new_tab(url)
            return {"status": "success", "message": f"Opened {url} in Firefox."}
            
        else:
            raise ProviderError(f"Unsupported browser action: {action}")
