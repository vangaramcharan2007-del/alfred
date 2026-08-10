"""Single composition root for Jarvis X runtime dependencies."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.kernel.health_coordinator import HealthCoordinator
from jarvisx.kernel.subsystem_manager import SubsystemManager
from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.memory.providers.cognee_provider import CogneeProvider
from jarvisx.memory.shared_memory import MockSQLiteProvider, SharedMemory
from jarvisx.runtime.event_bus import RuntimeEventBus
from jarvisx.runtime.state import RuntimeState
from jarvisx.security.permission_enforcer import PermissionEnforcer


@dataclass
class RuntimeMemoryFacade:
    """The existing shared and cognitive memory APIs owned by one runtime."""

    shared: SharedMemory
    cognitive: CognitiveMemory

    @classmethod
    def create(cls) -> "RuntimeMemoryFacade":
        return cls(
            shared=SharedMemory(provider=MockSQLiteProvider()),
            cognitive=CognitiveMemory(provider=CogneeProvider()),
        )


@dataclass
class RuntimeContext:
    """Owns runtime-wide dependencies and prevents split-brain initialization."""

    config_path: str = "config/jarvis.yaml"
    config: Dict[str, Any] = field(default_factory=dict)
    state: RuntimeState = field(default_factory=RuntimeState)
    event_bus: RuntimeEventBus = field(default_factory=RuntimeEventBus)
    subsystem_manager: SubsystemManager = field(default_factory=SubsystemManager)
    health_manager: Optional[HealthCoordinator] = None
    capability_registry: Optional[CapabilityRegistry] = None
    memory: Optional[RuntimeMemoryFacade] = None
    security: Optional[PermissionEnforcer] = None

    def __post_init__(self) -> None:
        if self.health_manager is None:
            self.health_manager = HealthCoordinator(self.subsystem_manager)
        if self.capability_registry is None:
            self.capability_registry = CapabilityRegistry(bus=self.event_bus)
        if self.memory is None:
            self.memory = RuntimeMemoryFacade.create()
        if self.security is None:
            self.security = PermissionEnforcer()

    @classmethod
    def create(cls, config_path: Optional[str] = None) -> "RuntimeContext":
        return cls(config_path=config_path or "config/jarvis.yaml")

    def bind_event_loop(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self.event_bus.bind_event_loop(loop)
