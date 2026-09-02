from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.llm.llm_provider import LLMProvider

class LLMRegistry:
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}

    def register(self, provider: LLMProvider) -> None:
        self.providers[provider.name] = provider

    def get(self, provider_id: str) -> Optional[LLMProvider]:
        return self.providers.get(provider_id)

    def list_providers(self) -> List[LLMProvider]:
        return list(self.providers.values())

    async def get_healthy_providers(self) -> List[LLMProvider]:
        healthy = []
        for p in self.providers.values():
            h = await p.health()
            if h.get("status") == "HEALTHY":
                healthy.append(p)
        return healthy
