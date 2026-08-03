from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.kernel.subsystem_manager import SubsystemManager
from jarvisx.kernel.lifecycle_manager import LifecycleManager
from jarvisx.kernel.event_orchestrator import EventOrchestrator
from jarvisx.kernel.health_coordinator import HealthCoordinator
from jarvisx.core.hermes import HermesBus
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.capabilities.coding.metrics import CodingMetrics

KERNEL_SUBSYSTEMS = [
    "capability_registry",
    "hermes_bus",
    "mcp_foundation",
    "memory_system",
    "llm_gateway",
    "provider_intelligence",
    "goose_runtime",
    "openhands_runtime",
    "github_engineering",
    "coding_agent",
    "architecture_agent",
    "meta_cognition",
    "evolution_engine",
    "brain_controller",
    "mission_system",
    "decision_engine",
    "voice_runtime",
]

class RuntimeKernel:
    def __init__(
        self,
        registry: Optional[CapabilityRegistry] = None,
        bus: Optional[HermesBus] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.registry = registry or CapabilityRegistry()
        self.bus = bus or HermesBus()
        self.metrics = metrics or CodingMetrics()

        self.subsystem_mgr = SubsystemManager()
        self.lifecycle = LifecycleManager(subsystem_manager=self.subsystem_mgr)
        self.event_orchestrator = EventOrchestrator(bus=self.bus)
        self.health_coordinator = HealthCoordinator(subsystem_manager=self.subsystem_mgr)

        # Register all subsystems
        for name in KERNEL_SUBSYSTEMS:
            self.subsystem_mgr.register_subsystem(name)

    def get_descriptors(self) -> List[CapabilityDescriptor]:
        return [
            CapabilityDescriptor(
                id="kernel.runtime",
                name="Jarvis X Runtime Kernel",
                version="1.0.0",
                author="Jarvis X",
                category="kernel",
                supported_actions=["boot", "shutdown", "health", "status", "recover"],
                handler=self.execute_kernel_action
            )
        ]

    async def register(self, registry: CapabilityRegistry) -> None:
        self.registry = registry
        for desc in self.get_descriptors():
            await registry.register(desc)

    async def boot(self) -> Dict[str, Any]:
        boot_res = await self.lifecycle.boot_all()

        await self.event_orchestrator.publish(
            "kernel.booted",
            "runtime_kernel",
            {"subsystems": boot_res["subsystems_online"], "duration": boot_res["boot_duration"]}
        )

        return boot_res

    async def shutdown(self) -> Dict[str, Any]:
        res = await self.lifecycle.shutdown_all()
        await self.event_orchestrator.publish(
            "kernel.shutdown",
            "runtime_kernel",
            {"state": res["state"]}
        )
        return res

    def health_check(self) -> Dict[str, Any]:
        return self.health_coordinator.run_health_check()

    def recover_components(self) -> Dict[str, Any]:
        return self.health_coordinator.recover_failed_components()

    def status(self) -> Dict[str, Any]:
        runtime = self.lifecycle.get_runtime_info()
        health = self.health_check()
        return {
            "runtime": runtime,
            "health": health
        }

    async def execute_kernel_action(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "boot":
            return await self.boot()
        elif action == "shutdown":
            return await self.shutdown()
        elif action == "health":
            return self.health_check()
        elif action == "status":
            return self.status()
        elif action == "recover":
            return self.recover_components()
        raise NotImplementedError(f"Action '{action}' not supported by RuntimeKernel.")

