#!/usr/bin/env python3
"""
Live Demonstration Script for Phase 34: Provider Intelligence Engine
Demonstrates task analysis, provider profiling, multi-factor scoring, intelligent provider selection,
simulated execution, failover rerouting, and outcome history learning.
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
from jarvisx.providers.intelligence.provider_selector import ProviderSelector
from jarvisx.providers.intelligence.provider_capabilities import TaskClassifier

async def event_logger(event: Event):
    t = event.type
    p = event.payload
    if t == "provider.selected":
        print(f"🎯 [HERMES EVENT] Selected Best Provider '{p.get('provider_id')}' (Score: {p.get('score')}) for task: '{p.get('task')}'")
    elif t == "provider.rejected":
        print(f"⚠️  [HERMES EVENT] Provider '{p.get('provider_id')}' Rejected/Failed. Reason: {p.get('reason')}")
    elif t == "provider.rerouted":
        print(f"🔄 [HERMES EVENT] Task Rerouted from Failed Provider '{p.get('failed_provider_id')}' to Fallback Provider.")

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("      JARVIS X - PHASE 34 PROVIDER INTELLIGENCE ENGINE DEMO")
    print("=" * 80)

    bus = HermesBus()
    bus.subscribe("provider.selected", event_logger)
    bus.subscribe("provider.rejected", event_logger)
    bus.subscribe("provider.rerouted", event_logger)

    registry = CapabilityRegistry(bus=bus)
    selector = ProviderSelector(bus=bus)
    await selector.register(registry)

    # Task 1: Complex FastAPI Auth Bug
    task_1 = "Fix critical memory leak and JWT auth refresh bug in FastAPI user service"
    print(f"\n💡 Task 1 Description: \"{task_1}\"")
    cat_1 = TaskClassifier.classify_task(task_1)
    print(f"   Automatic Classification: [{cat_1.value}]")

    print("\n📊 Step 1: Evaluating & Scoring Available Providers for Task 1...")
    rankings = selector.select_multiple(task_1, count=5, language="Python", framework="FastAPI")
    for rank, (profile, score) in enumerate(rankings, 1):
        print(f"   #{rank} [{profile.provider_id:<18}] Score: {score:<5} | Name: {profile.provider_name} (Success Rate: {profile.average_success_rate * 100}%)")

    print("\n🎯 Step 2: Intelligent Provider Selection...")
    selected_p, best_score = await selector.select_provider(task_1, language="Python", framework="FastAPI")
    print(f"   Chosen Provider: {selected_p.provider_name} (ID: {selected_p.provider_id}) with Score {best_score}")

    print("\n💥 Step 3: Simulating Primary Provider Execution Failure & Rerouting...")
    fallback_p, fallback_score = await selector.reroute(
        failed_provider_id=selected_p.provider_id,
        task_description=task_1,
        language="Python",
        framework="FastAPI"
    )
    print(f"   Rerouted to Fallback Provider: {fallback_p.provider_name} (ID: {fallback_p.provider_id}) with Score {fallback_score}")

    print("\n🧠 Step 4: Recording Learning Outcome in Provider History...")
    selector.history.record_outcome(
        provider_id=fallback_p.provider_id,
        task_description=task_1,
        success=True,
        runtime_seconds=1.25,
        language="Python",
        framework="FastAPI"
    )
    pref = selector.history.get_preferred_provider_for_language("python")
    print(f"   Updated History Preference for 'Python': {pref}")

    # Task 2: Architecture & Security Mission
    task_2 = "Audit system design and component security bounds for cloud deployment"
    print(f"\n💡 Task 2 Description: \"{task_2}\"")
    cat_2 = TaskClassifier.classify_task(task_2)
    print(f"   Automatic Classification: [{cat_2.value}]")

    selected_p2, score2 = await selector.select_provider(task_2, language="TypeScript", framework="React")
    print(f"   Chosen Provider for Task 2: {selected_p2.provider_name} (ID: {selected_p2.provider_id}) with Score {score2}")

    print("\n✨ Phase 34 Provider Intelligence Engine Demonstration Complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
