from __future__ import annotations

import time
from typing import Any, Optional

from jarvisx.core.capabilities.base import Capability, ProviderError
from jarvisx.core.capabilities.registry import SystemCapabilityRegistry
from jarvisx.core.logging import StructuredLogger


class CapabilityRuntime:
    """
    The execution environment for Capabilities.
    Alfred delegates task execution to this runtime.
    The runtime handles provider discovery, execution, retries, and fallbacks.
    """
    def __init__(self, registry: SystemCapabilityRegistry, logger: Optional[StructuredLogger] = None):
        self.registry = registry
        self.logger = logger or StructuredLogger()

    def execute(self, capability: Capability, task: dict[str, Any], max_retries: int = 1) -> dict[str, Any]:
        """
        Executes a task using the best available provider for the given capability.
        """
        provider = self.registry.resolve(capability)
        if not provider:
            self.logger.write("error", "capability.runtime.no_provider", capability=capability.name)
            raise ProviderError(f"No available provider for capability: {capability.name}")

        self.logger.write("info", "capability.runtime.execution_start", capability=capability.name, provider=provider.name)
        
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                result = provider.execute(task)
                self.logger.write("info", "capability.runtime.execution_success", capability=capability.name, provider=provider.name)
                return result
            except Exception as e:
                last_error = e
                self.logger.write("warning", "capability.runtime.execution_failed", 
                                  capability=capability.name, 
                                  provider=provider.name, 
                                  attempt=attempt + 1, 
                                  error=str(e))
                if attempt < max_retries:
                    time.sleep(1) # simple backoff
        
        # If we exhausted retries on the primary provider, try fallback providers
        all_providers = self.registry.get_all(capability)
        if len(all_providers) > 1:
            for fallback_provider in all_providers[1:]:
                try:
                    self.logger.write("info", "capability.runtime.fallback_attempt", capability=capability.name, provider=fallback_provider.name)
                    result = fallback_provider.execute(task)
                    self.logger.write("info", "capability.runtime.execution_success", capability=capability.name, provider=fallback_provider.name)
                    return result
                except Exception as e:
                    self.logger.write("warning", "capability.runtime.fallback_failed", capability=capability.name, provider=fallback_provider.name, error=str(e))

        raise ProviderError(f"Execution failed for capability {capability.name}. Last error: {str(last_error)}")
