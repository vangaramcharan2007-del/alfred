from __future__ import annotations

from typing import Optional

from jarvisx.core.providers.fallback_manager import FallbackManager
from jarvisx.core.providers.provider_registry import BaseProvider


class ProviderRouter:
    """
    Acts as the single point of entry for dispatching requests to the appropriate 
    active provider.
    """
    def __init__(self, fallback_manager: FallbackManager):
        self.fallback = fallback_manager
        
    def get_llm(self) -> Optional[BaseProvider]:
        return self.fallback.get_active("LLM")
        
    def get_tts(self) -> Optional[BaseProvider]:
        return self.fallback.get_active("TTS")
        
    def get_stt(self) -> Optional[BaseProvider]:
        return self.fallback.get_active("STT")
        
    def get_memory(self) -> Optional[BaseProvider]:
        return self.fallback.get_active("MEMORY")
        
    def get_vision(self) -> Optional[BaseProvider]:
        return self.fallback.get_active("VISION")
        
    async def route_with_failover(self, category: str, action: str, *args, **kwargs):
        """
        Executes an action on the active provider. If it fails, triggers failover
        and retries on the next provider.
        """
        provider = self.fallback.get_active(category)
        if not provider:
            raise RuntimeError(f"No active provider for {category}")
            
        try:
            # We assume providers implement the expected action method
            method = getattr(provider, action)
            return await method(*args, **kwargs)
        except Exception as e:
            # Trigger failover
            new_provider = await self.fallback.handle_failure(category, provider.capability.name)
            if not new_provider:
                raise RuntimeError(f"All providers for {category} failed. Last error: {e}")
                
            # Retry with new provider
            method = getattr(new_provider, action)
            return await method(*args, **kwargs)
