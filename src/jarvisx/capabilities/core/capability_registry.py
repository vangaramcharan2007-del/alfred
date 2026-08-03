from __future__ import annotations
import time
import inspect
from typing import Dict, Any, List, Optional, Callable
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.capabilities.core.capability_health import CapabilityHealthMonitor, CapabilityHealthReport
from jarvisx.capabilities.coding.metrics import CodingMetrics

class CapabilityRegistry:
    def __init__(
        self,
        bus: Optional[HermesBus] = None,
        health_monitor: Optional[CapabilityHealthMonitor] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.bus = bus or HermesBus()
        self.health_monitor = health_monitor or CapabilityHealthMonitor()
        self.metrics = metrics or CodingMetrics()
        self._capabilities: Dict[str, CapabilityDescriptor] = {}

    async def register(self, descriptor: CapabilityDescriptor) -> None:
        self._capabilities[descriptor.id] = descriptor
        self.health_monitor.register_capability(descriptor.id, descriptor.version)

        # Publish Hermes event
        await self.bus.publish(Event(
            type="capability.loaded",
            source="capability_registry",
            payload={"capability_id": descriptor.id, "name": descriptor.name, "category": descriptor.category}
        ))

    async def unregister(self, capability_id: str) -> bool:
        if capability_id in self._capabilities:
            del self._capabilities[capability_id]
            return True
        return False

    def get(self, capability_id: str) -> Optional[CapabilityDescriptor]:
        return self._capabilities.get(capability_id)

    def discover(self, category: Optional[str] = None, permission: Optional[str] = None) -> List[CapabilityDescriptor]:
        results = []
        for cap in self._capabilities.values():
            if category and cap.category != category:
                continue
            if permission and permission not in cap.permissions:
                continue
            results.append(cap)
        return results

    async def execute(self, capability_id: str, action: str, **kwargs) -> Any:
        start_time = time.time()
        cap = self.get(capability_id)
        if not cap:
            raise KeyError(f"Capability '{capability_id}' not found in registry.")

        if action not in cap.supported_actions and cap.supported_actions:
            raise ValueError(f"Action '{action}' not supported by capability '{capability_id}'.")

        if not cap.handler:
            raise NotImplementedError(f"No execution handler configured for capability '{capability_id}'.")

        try:
            if inspect.iscoroutinefunction(cap.handler):
                result = await cap.handler(action=action, **kwargs)
            else:
                result = cap.handler(action=action, **kwargs)

            latency_ms = (time.time() - start_time) * 1000.0
            self.health_monitor.record_execution(capability_id, success=True, latency_ms=latency_ms)
            return result
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000.0
            self.health_monitor.record_execution(capability_id, success=False, latency_ms=latency_ms)
            
            await self.bus.publish(Event(
                type="capability.failed",
                source="capability_registry",
                payload={"capability_id": capability_id, "action": action, "error": str(e)}
            ))
            raise e

    def health_check(self, capability_id: str) -> Optional[CapabilityHealthReport]:
        return self.health_monitor.get_report(capability_id)

    async def reload(self, capability_id: str) -> bool:
        cap = self.get(capability_id)
        if cap:
            cap.health_status = "HEALTHY"
            self.health_monitor.record_heartbeat(capability_id)
            return True
        return False

    def list_capabilities(self) -> List[CapabilityDescriptor]:
        return list(self._capabilities.values())
