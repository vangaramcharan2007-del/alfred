#!/usr/bin/env python3
"""
Live Demonstration Script for Phase 38: Autonomous Evolution Engine
Demonstrates meta weakness detection, improvement proposal creation, pre-execution upgrade simulation,
engineering mission planning, autonomous execution, sandbox testing, GitHub change commit creation, and evolution memory logging.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.meta.meta_engine import MetaCognitionEngine
from jarvisx.evolution.evolution_engine import AutonomousEvolutionEngine

async def event_logger(event: Event):
    t = event.type
    p = event.payload
    if t == "evolution.detected":
        print(f"💡 [HERMES EVENT] Evolution Opportunity Detected: '{p['proposal']['problem']}'")
    elif t == "evolution.planned":
        print(f"📋 [HERMES EVENT] Engineering Mission Planned: '{p['mission']['title']}' (Benefit: +{p['simulation']['expected_benefit_pct']}%)")
    elif t == "evolution.approval_required":
        print(f"⚠️  [HERMES EVENT] Safety Guard Approval Required: {p.get('reason')}")
    elif t == "evolution.started":
        print(f"🚀 [HERMES EVENT] Upgrade Execution Started for Proposal '{p.get('proposal_id')}'")
    elif t == "evolution.completed":
        print(f"✅ [HERMES EVENT] Upgrade Completed & Committed: '{p.get('commit')}'")

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("        JARVIS X - PHASE 38 AUTONOMOUS EVOLUTION ENGINE DEMO")
    print("=" * 80)

    bus = HermesBus()
    bus.subscribe("evolution.detected", event_logger)
    bus.subscribe("evolution.planned", event_logger)
    bus.subscribe("evolution.approval_required", event_logger)
    bus.subscribe("evolution.started", event_logger)
    bus.subscribe("evolution.completed", event_logger)

    registry = CapabilityRegistry(bus=bus)
    meta_engine = MetaCognitionEngine(registry=registry, bus=bus)
    await meta_engine.register(registry)

    evolution_engine = AutonomousEvolutionEngine(meta_engine=meta_engine, registry=registry, bus=bus)
    await evolution_engine.register(registry)

    # Pre-seed simulated degradation in Meta Engine for demonstration
    meta_engine.perf_monitor.record_capability_run("python.reviewer", success=False, duration_seconds=4.2)
    meta_engine.failure_memory.record_failure(
        task_description="Python code review lint accuracy",
        provider_id="local_linter",
        root_cause="Outdated AST parser rules",
        attempted_solution="Re-run regex parser",
        successful_fix="Integrate Ruff MCP Linter & AST Analyzer"
    )

    print("\n🧬 Step 1: Initiating Controlled Autonomous Evolution Cycle...")
    cycle_res = await evolution_engine.run_evolution_cycle()

    print("\n🔍 Step 2: Detected Weakness & Improvement Proposal...")
    prop = cycle_res["proposal"]
    print(f"   Proposal ID:       {prop['proposal_id']}")
    print(f"   Problem Statement: {prop['problem']}")
    print(f"   Proposed Solution: {prop['proposed_solution']}")
    print(f"   Priority / Risk:   Priority {prop['priority']} | Risk Level: {prop['risk_level']}")

    print("\n🔮 Step 3: Pre-Execution Upgrade Simulation...")
    sim = cycle_res["simulation"]
    print(f"   Expected Benefit:  +{sim['expected_benefit_pct']}%")
    print(f"   Dependency Risk:   {sim['dependency_risk']}")
    print(f"   Safety Score:      {sim['safety_score'] * 100}%")
    print(f"   Recommendation:    {sim['recommendation']}")

    print("\n🛡️  Step 4: Safety Guard Policy Evaluation...")
    guard = cycle_res["safety"]
    print(f"   Safe to Proceed:   {guard['safe']}")
    print(f"   Approval Required: {guard['approval_required']}")
    print(f"   Safety Reason:     {guard['reason']}")

    print("\n🗺️  Step 5: Engineering Mission & Implementation Plan...")
    mission = cycle_res["mission"]
    print(f"   Mission ID:        {mission['mission_id']}")
    print(f"   Target Component:  {mission['target_component']}")
    print("   Execution Roadmap:")
    for step in mission["steps"]:
        print(f"      • {step}")

    print("\n⚙️  Step 6: Autonomous Execution, Sandbox Validation & Commit...")
    exec_res = cycle_res["execution"]
    print(f"   Execution Status:  {exec_res['status']}")
    print(f"   Architecture Plan: {exec_res['architecture_plan']}")
    print(f"   Sandbox Test Run:  Command '{exec_res['test_results']['command']}' -> Output: {exec_res['test_results']['stdout']}")
    print(f"   Git Commit Created:{exec_res['commit_message']}")

    print("\n📚 Step 7: Evolution History & State Tracking...")
    state = cycle_res["state"]
    print(f"   Current Version:   {state['current_version']}")
    print(f"   Completed Upgrades:{state['previous_improvements_count']}")
    print(f"   System Risk Level: {state['risk_level']}")

    print("\n✨ Phase 38 Autonomous Evolution Engine Demonstration Complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
