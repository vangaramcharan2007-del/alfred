from __future__ import annotations

from typing import Any
import webbrowser
from jarvisx.core.capabilities.base import Capability, CapabilityProvider, ProviderError


class ChromeProvider(CapabilityProvider):
    name = "GoogleChrome"
    capability = Capability.BROWSER

    def is_available(self) -> bool:
        try:
            webbrowser.get("windows-default") # Just ensuring webbrowser module doesn't fail
            return True
        except webbrowser.Error:
            return False

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Executes a browser action using Chrome (via system default or specific path).
        task shape: {"action": "search" | "open_url", "query": "...", "url": "..."}
        """
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
