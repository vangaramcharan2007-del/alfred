#!/usr/bin/env python3
"""
Live Demonstration Script for Phase 31: Capability Registry + MCP Foundation + External Integration Layer
Demonstrates capability registration, provider connection, health monitoring, MCP server bridge,
capability discovery, and execution routing.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.core.capability_health import CapabilityHealthMonitor
from jarvisx.mcp.mcp_server_registry import MCPServerRegistry
from jarvisx.mcp.mcp_manager import MCPManager
from jarvisx.mcp.mcp_capability_bridge import MCPCapabilityBridge
from jarvisx.capabilities.external.external_provider import OllamaProvider, LiteLLMProvider, GooseProvider, OpenHandsProvider
from jarvisx.capabilities.external.provider_registry import ProviderRegistry
from jarvisx.capabilities.external.provider_router import ProviderRouter

async def event_logger(event: Event):
    t = event.type
    p = event.payload
    if t == "capability.loaded":
        print(f"📦 [HERMES EVENT] Capability Registered: '{p.get('capability_id')}' ({p.get('category')})")
    elif t == "provider.connected":
        print(f"🔌 [HERMES EVENT] External Provider Connected: '{p.get('provider')}'")
    elif t == "mcp.server.connected":
        print(f"⚡ [HERMES EVENT] MCP Server Connected: '{p.get('server_name')}' ({p.get('server_type')})")


async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("  JARVIS X - PHASE 31 CAPABILITY REGISTRY & MCP INTEGRATION FOUNDATION DEMO")
    print("=" * 80)

    bus = HermesBus()
    bus.subscribe("capability.loaded", event_logger)
    bus.subscribe("provider.connected", event_logger)
    bus.subscribe("mcp.server.connected", event_logger)

    health_monitor = CapabilityHealthMonitor()
    cap_registry = CapabilityRegistry(bus=bus, health_monitor=health_monitor)

    # Step 1: Register Core Coding Capability
    print("\n📝 Step 1: Registering Internal Core Coding Agent Capability...")
    async def _coding_handler(action: str, **kwargs):
        return {"action": action, "status": "executed", "details": kwargs}

    core_cap = CapabilityDescriptor(
        id="coding.agent",
        name="Jarvis X Autonomous Coding Agent",
        version="1.0.0",
        category="coding",
        permissions=["READ", "WRITE", "EXECUTE"],
        supported_actions=["analyze", "plan", "execute_repair", "review"],
        handler=_coding_handler
    )
    await cap_registry.register(core_cap)

    # Step 2: External Providers Connection
    print("\n🔌 Step 2: Registering External AI Framework Providers (Ollama, LiteLLM, Goose, OpenHands)...")
    provider_registry = ProviderRegistry(bus=bus)
    await provider_registry.register_provider(OllamaProvider())
    await provider_registry.register_provider(LiteLLMProvider())
    await provider_registry.register_provider(GooseProvider())
    await provider_registry.register_provider(OpenHandsProvider())

    # Step 3: MCP Server Connections & Capability Bridge
    print("\n⚡ Step 3: Connecting Model Context Protocol (MCP) Servers & Bridging to Capability Registry...")
    server_registry = MCPServerRegistry()
    mcp_manager = MCPManager(bus=bus, server_registry=server_registry)
    mcp_bridge = MCPCapabilityBridge(mcp_manager=mcp_manager, capability_registry=cap_registry)

    # Bridge MCP Filesystem, GitHub, Docker, SQLite, Postgres, Playwright, Terminal
    for s_name in ["filesystem", "github", "docker", "sqlite", "postgres", "playwright", "terminal"]:
        await mcp_bridge.bridge_server(s_name)

    # Step 4: Capability Discovery
    print("\n🔍 Step 4: Discovering Capabilities in Registry...")
    mcp_caps = cap_registry.discover(category="mcp")
    print(f"   Found {len(mcp_caps)} MCP capabilities registered.")
    for cap in mcp_caps:
        print(f"   - [{cap.id}] {cap.name} (Actions: {cap.supported_actions})")

    # Step 5: Execution Routing & Health Checks
    print("\n⚙️  Step 5: Testing Execution Routing & Health Monitoring...")
    # Execute MCP Filesystem tool
    exec_mcp_res = await cap_registry.execute("mcp.filesystem", "filesystem_action", target_dir="./src")
    print(f"   MCP Execution Output: {json.dumps(exec_mcp_res)}")

    # Route execution to Ollama provider
    router = ProviderRouter(registry=provider_registry)
    ollama_res = await router.route_execution("ollama", "generate", prompt="Explain micro-VM sandboxing")
    print(f"   Provider Route Output: {json.dumps(ollama_res)}")

    # Step 6: Health Monitor Status
    print("\n🩺 Step 6: Querying Capability Health Reports...")
    for report in health_monitor.list_reports():
        print(f"   - Capability [{report.capability_id}]: Status={report.status}, Latency={report.response_latency_ms}ms, Failures={report.execution_failures}")

    print("\n✨ Phase 31 Capability Registry & MCP Integration Foundation Demo Complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
