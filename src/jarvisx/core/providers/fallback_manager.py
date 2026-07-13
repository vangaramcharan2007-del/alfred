from __future__ import annotations

import asyncio
from typing import Dict, Optional, Any

from jarvisx.core.providers.provider_registry import ProviderRegistry, BaseProvider


class FallbackManager:
    """
    Maintains the state of which provider is currently active for each category.
    Detects failures and automatically transitions to the next available provider.
    """
    def __init__(self, registry: ProviderRegistry):
        self.registry = registry
        # Current active provider name by category
        self.active_providers: Dict[str, BaseProvider] = {}
        # Keep track of failed providers and their last failure time
        self.failed_providers: Dict[str, float] = {}

    async def initialize(self) -> None:
        """Find the best available provider for each category on startup."""
        for category in self.registry.get_all_categories():
            await self.failover(category)

    async def failover(self, category: str) -> Optional[BaseProvider]:
        """
        Attempts to find the highest-priority healthy provider for a category.
        Sets it as the active provider and returns it.
        """
        providers = self.registry.get_providers(category)
        
        for provider in providers:
            # Check if it's healthy
            is_healthy = await provider.check_health()
            if is_healthy:
                self.active_providers[category] = provider
                return provider
                
        # If all fail, we have no active provider for this category
        self.active_providers.pop(category, None)
        return None

    def get_active(self, category: str) -> Optional[BaseProvider]:
        return self.active_providers.get(category)
        
    async def handle_failure(self, category: str, failed_provider_name: str) -> Optional[BaseProvider]:
        """
        Called when a provider fails during a runtime request.
        Triggers a failover if the failed provider is currently the active one.
        """
        import time
        self.failed_providers[failed_provider_name] = time.time()
        
        current = self.active_providers.get(category)
        if current and current.capability.name == failed_provider_name:
            # The active provider failed, we need to failover
            return await self.failover(category)
            
        return current
