#!/usr/bin/env python3
"""
Live Demonstration Script for Phase 37: Jarvis X Meta-Cognition Engine
Demonstrates capability scanning, system knowledge graph building, performance analysis, weakness detection,
self-improvement plan generation, evolution memory recording, and decision confidence scoring.
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

async def event_logger(event: Event):
    t = event.type
    p = event.payload
    if t == "meta.capability.discovered":
        print(f"🔍 [HERMES EVENT] Discovered {p.get('count')} Registered Capabilities in System")
    elif t == "meta.knowledge.gap.detected":
        print(f"⚠️  [HERMES EVENT] Knowledge Gap / Degradation Detected: {p.get('degraded')}")
    elif t == "meta.improvement.planned":
        print(f"🛠️  [HERMES EVENT] Formulated {p.get('plans_count')} Self-Improvement Missions")
    elif t == "meta.self_analysis.completed":
        print(f"✅ [HERMES EVENT] Self-Analysis Completed in {p.get('duration')}s (Confidence: {p.get('confidence') * 100}%)")

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("        JARVIS X - PHASE 37 META-COGNITION & SELF-IMPROVEMENT ENGINE DEMO")
    print("=" * 80)

    bus = HermesBus()
    bus.subscribe("meta.capability.discovered", event_logger)
    bus.subscribe("meta.knowledge.gap.detected", event_logger)
    bus.subscribe("meta.improvement.planned", event_logger)
    bus.subscribe("meta.self_analysis.completed", event_logger)

    registry = CapabilityRegistry(bus=bus)
    meta_engine = MetaCognitionEngine(registry=registry, bus=bus)
    await meta_engine.register(registry)

    # Simulate past performance & failures for demonstration
    meta_engine.perf_monitor.record_capability_run("java.debugger", success=False, duration_seconds=3.5)
    meta_engine.failure_memory.record_failure(
        task_description="Refactor Java microservice dependency injection",
        provider_id="openhands",
        root_cause="Missing Java AST Parser & Maven MCP daemon",
        attempted_solution="Re-run compilation build",
        successful_fix="Add Java AST parser & Maven MCP tool"
    )

    print("\n🧠 Step 1: Initiating Full System Self-Analysis...")
    analysis_res = await meta_engine.run_self_analysis()

    print(f"\n📊 Step 2: System Capability Introspection...")
    cap_sum = analysis_res["capabilities_summary"]
    print(f"   Total Registered Capabilities: {cap_sum['total_capabilities']}")
    print(f"   Capability Categories:        {cap_sum['categories']}")

    print("\n🕸️  Step 3: System Knowledge Graph Construction...")
    sg = analysis_res["system_graph"]
    print(f"   Graph Node Entities:          {sg['nodes_count']}")
    print(f"   Graph Relationship Edges:     {sg['edges_count']}")

    print("\n🛠️  Step 4: Prioritized Self-Improvement Plan Generation...")
    plans = analysis_res["improvement_plans"]
    for i, plan in enumerate(plans, 1):
        print(f"   Mission #{i} [Priority {plan['priority']}]: {plan['title']}")
        print(f"      Problem: {plan['problem_statement']}")
        print(f"      Action Items: {plan['action_items']}")

    print("\n🎯 Step 5: Decision Enhancement & Self-Awareness Confidence Evaluation...")
    # Mission A: High capability match
    task_a = "Design microservice architecture and generate GitHub Pull Request"
    eval_a = meta_engine.decision_engine.evaluate_task_execution(task_a)
    print(f"   Task A: \"{task_a}\"")
    print(f"      Self-Awareness Score: {eval_a['self_awareness_score']}")
    print(f"      Capability Confidence: {eval_a['capability_confidence'] * 100}%")
    print(f"      Can Proceed:          {eval_a['can_proceed']}")

    # Mission B: Missing capability (Mobile app)
    task_b = "Build mobile iOS application with end to end UI testing"
    eval_b = meta_engine.decision_engine.evaluate_task_execution(task_b)
    print(f"\n   Task B: \"{task_b}\"")
    print(f"      Missing Capabilities:  {eval_b['missing_capabilities']}")
    print(f"      Knowledge Gap Score:   {eval_b['knowledge_gap_score']}")
    print(f"      Capability Confidence: {eval_b['capability_confidence'] * 100}%")
    print(f"      Recommendations:       {eval_b['recommendations']}")

    print("\n✨ Phase 37 Meta-Cognition & Self-Improvement Engine Demonstration Complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
