"""Regression coverage for the Phase 104.9 runtime composition root."""

from __future__ import annotations

import asyncio

from jarvisx.multi_agent.alfred_master import AlfredMasterCoordinator
from jarvisx.runtime.runtime import JarvisRuntime


class InMemoryAgentBus:
    def subscribe(self, recipient, callback):
        self.recipient = recipient
        self.callback = callback


def test_runtime_uses_one_shared_context(tmp_path):
    runtime = JarvisRuntime(config_path=str(tmp_path / "missing-config.yaml"))

    state = asyncio.run(runtime.start(print_banner=False))
    coordinator = AlfredMasterCoordinator(
        bus=InMemoryAgentBus(),
        context=runtime.context,
    )

    assert state.state_name == "RUNNING"
    assert runtime.bootstrap.context is runtime.context
    assert runtime.kernel.context is runtime.context
    assert runtime.daemon.context is runtime.context
    assert runtime.alfred.context is runtime.context
    assert runtime.cli.context is runtime.context
    assert coordinator.context is runtime.context

    assert runtime.kernel.bus is runtime.context.event_bus
    assert runtime.daemon.event_bus is runtime.context.event_bus
    assert runtime.alfred.bus is runtime.context.event_bus
    assert coordinator.event_bus is runtime.context.event_bus

    assert runtime.kernel.registry is runtime.context.capability_registry
    assert runtime.daemon.capability_registry is runtime.context.capability_registry
    assert runtime.alfred.registry is runtime.context.capability_registry
    assert coordinator.registry is runtime.context.capability_registry

    assert runtime.kernel.memory is runtime.context.memory
    assert runtime.daemon.memory is runtime.context.memory
    assert runtime.alfred.memory is runtime.context.memory
    assert coordinator.memory is runtime.context.memory

    assert runtime.kernel.security is runtime.context.security
    assert runtime.daemon.security is runtime.context.security
    assert runtime.alfred.security is runtime.context.security
    assert coordinator.security is runtime.context.security
    assert runtime.kernel.health_coordinator is runtime.context.health_manager
    assert runtime.daemon.health_manager is runtime.context.health_manager

    asyncio.run(runtime.stop())
