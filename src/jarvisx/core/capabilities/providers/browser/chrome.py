from __future__ import annotations

from typing import Any
import os
import webbrowser
from jarvisx.core.capabilities.base import Capability, CapabilityProvider, ProviderError
from jarvisx.core.capabilities.evaluation import ProviderEvaluation


class ChromeProvider(CapabilityProvider):
    name = "GoogleChrome"
    capability = Capability.BROWSER

    def is_available(self) -> bool:
        if os.environ.get("MOCK_CHROME_UNAVAILABLE") == "1":
            return False
        try:
            webbrowser.get("windows-default") # Just ensuring webbrowser module doesn't fail
            return True
        except webbrowser.Error:
            return False

    def evaluate(self, task: dict[str, Any]) -> ProviderEvaluation:
        available = self.is_available()
        return ProviderEvaluation(
            provider_name=self.name,
            capability=self.capability.name,
            score=98.0 if available else 0.0,
            available=available,
            confidence=1.0 if available else 0.0,
            latency_ms=30.0,
            reason="Installed, default browser, full capability support" if available else "Browser missing"
        )

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Executes a browser action using Chrome (via system default or specific path).
        task shape: {"action": "search" | "open_url", "query": "...", "url": "..."}
        """
        if os.environ.get("MOCK_CHROME_FAIL") == "1":
            raise ProviderError("Simulated Chrome execution failure (e.g. process crashed).")
            
        action = task.get("action")

        if action == "search":
            query = task.get("query")
            if not query:
                raise ProviderError("Browser search task requires 'query'.")
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open_new_tab(url)
            return {"status": "success", "message": f"Searched for '{query}' in Chrome."}
            
        elif action == "open_url":
            url = task.get("url")
            if not url:
                raise ProviderError("Browser open_url task requires 'url'.")
            webbrowser.open_new_tab(url)
            return {"status": "success", "message": f"Opened {url} in Chrome."}
            
        else:
            raise ProviderError(f"Unsupported browser action: {action}")

    def verify(self, task: dict[str, Any]) -> bool:
        """
        Verify if the browser task succeeded.
        For browser, since we fire-and-forget webbrowser, we can't easily check process.
        We'll just return True or check if OS mock fails.
        """
        if os.environ.get("MOCK_CHROME_FAIL") == "1":
            return False
        return True
