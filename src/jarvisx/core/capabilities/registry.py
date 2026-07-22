from __future__ import annotations

import importlib
import inspect
import os
import pkgutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from jarvisx.core.capabilities.base import Capability, CapabilityProvider
from jarvisx.core.capabilities.evaluation import ProviderEvaluation
from jarvisx.core.capabilities.negotiation import NegotiationStrategy, HighestScoreStrategy
from jarvisx.core.logging import StructuredLogger
from dataclasses import dataclass

@dataclass
class ProviderCandidate:
    provider: CapabilityProvider
    score: float
    reason: str


class SystemCapabilityRegistry:
    """
    Discovers and registers Capability Providers dynamically.
    Caches availability during startup to prevent slow scanning.
    """
    def __init__(self, logger: Optional[StructuredLogger] = None):
        self.logger = logger or StructuredLogger()
        self._providers: Dict[Capability, List[CapabilityProvider]] = {cap: [] for cap in Capability}
        self._initialized = False

    def discover_plugins(self, plugins_dir: Path) -> None:
        """
        Dynamically scans a directory for provider implementations and registers them.
        This allows new apps (e.g. Chrome, WhatsApp) to be dropped in without changing Alfred.
        """
        if not plugins_dir.exists():
            return

        for root, _, files in os.walk(plugins_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    module_path = Path(root) / file
                    try:
                        self._load_module(module_path)
                    except Exception as e:
                        self.logger.write("warning", "capability.plugin.load_failed", file=file, error=str(e))
        self._initialized = True

    def _load_module(self, path: Path) -> None:
        """Dynamically imports a module and registers any Provider classes found."""
        # Convert path to module string: src/jarvisx/core/capabilities/providers/chrome.py -> jarvisx.core.capabilities.providers.chrome
        try:
            rel_path = path.absolute().relative_to((Path.cwd() / "src").absolute())
        except ValueError:
            # Fallback if not in standard src structure
            rel_path = path
        
        module_name = str(rel_path.with_suffix("")).replace(os.sep, ".")
        if module_name.startswith("jarvisx."):
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, CapabilityProvider) and obj is not CapabilityProvider:
                    provider_instance = obj()
                    if provider_instance.is_available():
                        self.register(provider_instance)

    def register(self, provider: CapabilityProvider) -> None:
        """Manually registers a provider."""
        self._providers[provider.capability].append(provider)
        self.logger.write("info", "capability.registered", capability=provider.capability.name, provider=provider.name)

    def resolve(self, capability: Capability) -> Optional[CapabilityProvider]:
        """Returns the first available provider for a capability (Legacy fallback)."""
        providers = self._providers.get(capability, [])
        return providers[0] if providers else None
        
    def negotiate(
        self, 
        capability: Capability, 
        task: dict[str, Any], 
        strategy: Optional[NegotiationStrategy] = None
    ) -> List[ProviderCandidate]:
        """
        Dynamically asks all providers to bid on a task, applies learning metrics, 
        and uses a strategy to rank them for fallback execution.
        """
        providers = self._providers.get(capability, [])
        if not providers:
            return []
            
        strategy = strategy or HighestScoreStrategy()
        evaluations: List[ProviderEvaluation] = []
        
        for provider in providers:
            # Phase 1: Fast synchronous evaluation
            try:
                eval_obj = provider.evaluate(task)
                
                # Inject runtime health/learning metrics into the evaluation
                eval_obj.health_status = provider.health.status
                eval_obj.success_rate = provider.health.success_rate
                
                evaluations.append(eval_obj)
            except Exception as e:
                self.logger.write("warning", "capability.evaluation_failed", provider=provider.name, error=str(e))
                
        ranked_evals = strategy.rank(evaluations)
        candidates = []
        
        for eval_obj in ranked_evals:
            # Match the evaluation back to the provider instance
            for p in providers:
                if p.name == eval_obj.provider_name:
                    candidates.append(ProviderCandidate(
                        provider=p,
                        score=eval_obj.score,
                        reason=eval_obj.reason
                    ))
                    break
                    
        return candidates

    def get_all(self, capability: Capability) -> List[CapabilityProvider]:
        """Returns all registered providers for a capability."""
        return self._providers.get(capability, [])
