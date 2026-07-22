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
        Executes a task by trying the best available provider, falling back to the next
        best candidate if execution fails.
        """
        candidates = self.registry.negotiate(capability, task)
        if not candidates:
            self.logger.write("error", "capability.runtime.no_provider", capability=capability.name)
            raise ProviderError(f"No available provider for capability: {capability.name}")

        last_error = None
        for candidate in candidates:
            provider = candidate.provider
            self.logger.write("info", "capability.runtime.execution_start", capability=capability.name, provider=provider.name)
            
            for attempt in range(max_retries + 1):
                try:
                    start_time = time.time()
                    result = provider.execute(task)
                    latency = (time.time() - start_time) * 1000
                    
                    if not provider.verify(task):
                        raise ProviderError(f"Execution succeeded but verification failed for {provider.name}")
                        
                    provider.health.record_success(latency)
                    self.logger.write("info", "capability.runtime.execution_success", capability=capability.name, provider=provider.name, latency_ms=latency)
                    return result
                except Exception as e:
                    provider.health.record_failure()
                    last_error = e
                    self.logger.write("warning", "capability.runtime.execution_failed", 
                                      capability=capability.name, 
                                      provider=provider.name, 
                                      attempt=attempt + 1, 
                                      error=str(e),
                                      health_status=provider.health.status.value)
                    if attempt < max_retries:
                        time.sleep(1) # simple backoff
            
            # If we exhausted retries for this provider, the loop continues to the next candidate
            self.logger.write("info", "capability.runtime.fallback_trigger", capability=capability.name, failed_provider=provider.name)

        raise ProviderError(f"Execution failed for capability {capability.name} after trying {len(candidates)} providers. Last error: {str(last_error)}")
