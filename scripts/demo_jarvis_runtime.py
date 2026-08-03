#!/usr/bin/env python3
"""
Live Demonstration Script for Phase 39: Jarvis X Unified Autonomous Operating System
Demonstrates kernel boot, subsystem health, brain intent analysis, unified decision making,
autonomous mission execution, GitHub PR simulation, evolution check, and CLI commands.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.kernel.runtime_kernel import RuntimeKernel
from jarvisx.brain.brain_controller import BrainController
from jarvisx.missions.mission_manager import MissionManager
from jarvisx.decision.decision_context import DecisionContext
from jarvisx.decision.unified_decision_engine import UnifiedDecisionEngine
from jarvisx.meta.meta_engine import MetaCognitionEngine
from jarvisx.evolution.evolution_engine import AutonomousEvolutionEngine
from jarvisx.interface.cli import JarvisCLI

async def event_logger(event: Event):
    t = event.type
    p = event.payload
    if t == "kernel.booted":
        print(f"⚡ [HERMES] Kernel Booted: {p['subsystems']} subsystems online in {p['duration']}s")
    elif t == "brain.intent.analyzed":
        print(f"🧠 [HERMES] Intent Analyzed: '{p['intent']}' (Confidence: {p['confidence'] * 100}%)")
    elif t == "brain.request.processed":
        print(f"📡 [HERMES] Request Routed: Capability={p['capability']} Provider={p['provider']}")
    elif t == "mission.created":
        print(f"🚀 [HERMES] Mission Created: {p['mission_id']} (Intent: {p['intent']})")
    elif t == "mission.completed":
        print(f"✅ [HERMES] Mission Completed: {p['mission_id']} (Status: {p['status']})")

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("      JARVIS X - PHASE 39 UNIFIED AUTONOMOUS OPERATING SYSTEM DEMO")
    print("=" * 80)

    # Wire up HermesBus
    bus = HermesBus()
    for evt in ["kernel.booted", "brain.intent.analyzed", "brain.request.processed", "mission.created", "mission.completed"]:
        bus.subscribe(evt, event_logger)

    registry = CapabilityRegistry(bus=bus)

    # === STEP 1: Boot Runtime Kernel ===
    print("\n⚡ Step 1: Booting Jarvis X Runtime Kernel...")
    kernel = RuntimeKernel(registry=registry, bus=bus)
    await kernel.register(registry)
    boot_res = await kernel.boot()
    print(f"   State:              {boot_res['state']}")
    print(f"   Subsystems Online:  {boot_res['subsystems_online']}")
    print(f"   Boot Duration:      {boot_res['boot_duration']}s")

    # === STEP 2: System Health Check ===
    print("\n💚 Step 2: Running Full System Health Check...")
    health = kernel.health_check()
    print(f"   Overall Health:     {health['overall']}")
    print(f"   Health Score:       {health['health_score'] * 100}%")
    print(f"   Online:             {health['online']}/{health['total_subsystems']}")
    print(f"   Degraded:           {health['degraded_count']}")

    # === STEP 3: Brain Processes User Request ===
    user_request = "Create a productivity app with task management and calendar"
    print(f"\n🧠 Step 3: Brain Processing Request: \"{user_request}\"")
    brain = BrainController(registry=registry, bus=bus)
    await brain.register(registry)
    brain_res = await brain.process_request(user_request)
    print(f"   Detected Intent:    {brain_res['intent']['intent']}")
    print(f"   Intent Confidence:  {brain_res['intent']['confidence'] * 100}%")
    print(f"   Target Capability:  {brain_res['route']['capability']}")
    print(f"   Target Provider:    {brain_res['route']['preferred_provider']}")

    # === STEP 4: Unified Decision Engine ===
    print("\n🎯 Step 4: Unified Decision Engine Evaluation...")
    decision_engine = UnifiedDecisionEngine(registry=registry)
    await decision_engine.register(registry)
    ctx = DecisionContext(
        task_description=user_request,
        intent=brain_res["intent"]["intent"]
    )
    decision = decision_engine.decide(ctx)
    explanation = decision_engine.explainer.explain(decision)
    print(f"   Capability:         {decision['capability']}")
    print(f"   Provider:           {decision['provider']}")
    print(f"   Local Model:        {decision['model']}")
    print(f"   Risk:               {decision['risk']}")
    print(f"   Confidence:         {decision['confidence'] * 100}%")
    print(f"   Reasons:")
    for r in decision["reasons"]:
        print(f"      - {r}")

    # === STEP 5: Autonomous Mission Execution ===
    print(f"\n🚀 Step 5: Executing Autonomous Mission: \"{user_request}\"")
    mission_mgr = MissionManager(brain=brain, registry=registry, bus=bus)
    await mission_mgr.register(registry)
    mission_res = await mission_mgr.create_and_execute_mission(user_request)
    m = mission_res["mission"]
    r = mission_res["result"]
    print(f"   Mission ID:         {m['mission_id']}")
    print(f"   Status:             {m['status']}")
    print(f"   Architecture:       {r['architecture']}")
    print(f"   Provider Output:    {r['provider_output']['output'][:60]}...")
    print(f"   Sandbox Test:       {r['test_result']['stdout']}")
    print(f"   GitHub PR:          PR #{r['github_pr']['pr_number']} - {r['github_pr']['title']}")
    print(f"   Mission Steps:")
    for step in m["steps"]:
        print(f"      ✓ {step}")

    # === STEP 6: Meta-Cognition Self Analysis ===
    print("\n🔬 Step 6: Meta-Cognition Self Analysis...")
    meta_engine = MetaCognitionEngine(registry=registry, bus=bus)
    await meta_engine.register(registry)
    meta_res = await meta_engine.run_self_analysis()
    print(f"   Registered Capabilities: {meta_res['capabilities_summary']['total_capabilities']}")
    print(f"   System Confidence:       {meta_res['confidence'] * 100}%")

    # === STEP 7: CLI Interface Demo ===
    print("\n💻 Step 7: CLI Interface Commands...")
    cli = JarvisCLI(kernel=kernel)
    help_res = cli.handle_command("help")
    print("   Available CLI Commands:")
    for cmd, desc in help_res["commands"].items():
        print(f"      jarvis {cmd:12s} - {desc}")

    print("\n✨ Phase 39 Unified Autonomous Operating System Demonstration Complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
