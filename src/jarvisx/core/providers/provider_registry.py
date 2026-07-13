from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ProviderCapability:
    category: str  # e.g., "LLM", "TTS", "STT", "MEMORY", "VISION"
    name: str      # e.g., "openai", "elevenlabs", "local_model"
    priority: int  # lower number = higher priority
    is_local: bool # true if it can run offline


class BaseProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def capability(self) -> ProviderCapability:
        pass
        
    @abc.abstractmethod
    async def check_health(self) -> bool:
        """Returns True if the provider is currently reachable and configured."""
        pass
        
    @abc.abstractmethod
    async def benchmark(self) -> float:
        """Returns the latency in milliseconds. Returns float('inf') if unreachable."""
        pass


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, List[BaseProvider]] = {}
        
    def register(self, provider: BaseProvider) -> None:
        cap = provider.capability
        if cap.category not in self._providers:
            self._providers[cap.category] = []
            
        self._providers[cap.category].append(provider)
        # Sort by priority (ascending)
        self._providers[cap.category].sort(key=lambda p: p.capability.priority)
        
    def get_providers(self, category: str) -> List[BaseProvider]:
        """Returns the ordered list of providers for a category."""
        return self._providers.get(category, [])
        
    def get_all_categories(self) -> List[str]:
        return list(self._providers.keys())
