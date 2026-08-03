from __future__ import annotations
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.external.provider_registry import ProviderRegistry
from jarvisx.capabilities.external.external_provider import Provider

class ProviderRouter:
    def __init__(
        self,
        registry: Optional[ProviderRegistry] = None,
        config_path: Optional[str] = None
    ):
        self.registry = registry or ProviderRegistry()
        self.config_path = config_path or "config/providers.yaml"
        self.provider_configs: Dict[str, Dict[str, Any]] = self._load_config()

    def _load_config(self) -> Dict[str, Dict[str, Any]]:
        path = Path(self.config_path)
        if path.exists():
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                return data
            except Exception:
                pass
        # Default configuration
        return {
            "ollama": {"enabled": True},
            "litellm": {"enabled": True},
            "openrouter": {"enabled": False},
            "openhands": {"enabled": False},
            "goose": {"enabled": False}
        }

    def is_provider_enabled(self, provider_name: str) -> bool:
        conf = self.provider_configs.get(provider_name.lower(), {})
        return conf.get("enabled", True)

    async def route_execution(self, provider_name: str, action: str, **kwargs) -> Any:
        if not self.is_provider_enabled(provider_name):
            raise PermissionError(f"Provider '{provider_name}' is disabled in configuration.")

        provider = self.registry.get_provider(provider_name)
        if not provider:
            raise KeyError(f"Provider '{provider_name}' is not registered or connected.")

        return await provider.execute(action, **kwargs)

    def find_provider_for_capability(self, capability: str) -> Optional[Provider]:
        for provider in self.registry.list_providers():
            if self.is_provider_enabled(provider.name) and capability in provider.capabilities():
                return provider
        return None
