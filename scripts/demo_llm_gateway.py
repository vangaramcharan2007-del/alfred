#!/usr/bin/env python3
"""
Live Demonstration Script for Phase 36: Zero-Cost Local-First LLM Intelligence Gateway
Demonstrates hardware detection, Ollama model discovery, OmniRoute health checks, task classification,
model scoring, primary selection, response generation, simulated provider failure, automatic fallback, and outcome learning.
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
from jarvisx.llm.llm_manager import LLMManager
from jarvisx.llm.llm_scoring import HardwareMonitor, LLMTaskClassifier

async def event_logger(event: Event):
    t = event.type
    p = event.payload
    if t == "llm.request.started":
        print(f"🚀 [HERMES EVENT] LLM Gateway Request Started (Prompt: '{p.get('prompt')}', Offline: {p.get('require_offline')})")
    elif t == "llm.model.selected":
        print(f"🎯 [HERMES EVENT] Selected Model '{p.get('model')}' from Provider '{p.get('provider')}' (Score: {p.get('score')})")
    elif t == "llm.response.completed":
        print(f"✅ [HERMES EVENT] LLM Response Completed for Model '{p.get('model')}' in {p.get('duration')}s")

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("   JARVIS X - PHASE 36 ZERO-COST LOCAL-FIRST LLM INTELLIGENCE GATEWAY DEMO")
    print("=" * 80)

    bus = HermesBus()
    bus.subscribe("llm.request.started", event_logger)
    bus.subscribe("llm.model.selected", event_logger)
    bus.subscribe("llm.response.completed", event_logger)

    registry = CapabilityRegistry(bus=bus)
    manager = LLMManager(bus=bus)
    await manager.register(registry)

    print("\n💻 Step 1: Hardware Intelligence & Spec Detection...")
    hw_info = await registry.execute("llm.analysis", "detect_hardware")
    hw = hw_info["hardware"]
    print(f"   CPU Cores:         {hw['cpu_cores']}")
    print(f"   RAM:               {hw['ram_gb']} GB")
    print(f"   GPU Available:     {hw['gpu_available']} (VRAM: {hw['vram_gb']} GB)")

    print("\n🔍 Step 2: Provider & Model Discovery...")
    ollama_provider = manager.router.registry.get("ollama.local")
    omniroute_provider = manager.router.registry.get("omniroute.gateway")
    ollama_health = await ollama_provider.health()
    omniroute_health = await omniroute_provider.health()
    print(f"   [Ollama Local]      Status: {ollama_health['status']} | Installed Models: {ollama_health['installed_models'][:2]}")
    print(f"   [OmniRoute Gateway] Status: {omniroute_health['status']} | Available Models: {omniroute_health['available_models'][:2]}")

    # Task 1: Offline Coding Task
    prompt_1 = "Write a high-performance Python async queue processor with error retry handling"
    print(f"\n💡 Task 1 Prompt: \"{prompt_1}\"")
    cat_1 = LLMTaskClassifier.classify_request(prompt_1)
    print(f"   Automatic Task Classification: [{cat_1}]")

    print("\n📊 Step 3: Scoring Available LLM Models for Task 1...")
    rankings_1 = manager.router.compare_models(prompt_1, count=5)
    for rank, item in enumerate(rankings_1, 1):
        p = item["profile"]
        s = item["score"]
        print(f"   #{rank} [{p['model_name']:<24}] Provider: {p['provider_id']:<18} Score: {s:<5} (Cost: ${p['cost']})")

    print("\n🎯 Step 4: Routing Request to Best Model (Local Offline Mandatory)...")
    res_1 = await registry.execute(
        "llm.gateway",
        "generate",
        prompt=prompt_1,
        require_offline=True
    )
    print(f"   Selected Model:    {res_1['selected_model']}")
    print(f"   Response Snippet:  {res_1['result']['response'][:90]}...")

    # Task 2: Simulated Primary Failure & Automatic Fallback
    print("\n💥 Step 5: Simulating Model Failure & Automatic Fallback...")
    fallback_p, fallback_s = manager.router.fallback_model(res_1['selected_model'], prompt_1)
    print(f"   Fallback Triggered from '{res_1['selected_model']}' -> '{fallback_p.model_name}' (Provider: {fallback_p.provider_id}, Score: {fallback_s})")

    print("\n🧠 Step 6: Storing Learning & Task Affinity...")
    manager.router.history.record_outcome(
        provider_id=fallback_p.provider_id,
        model_name=fallback_p.model_name,
        task_category=cat_1,
        success=True,
        latency=0.18
    )
    pref_model = manager.router.history.get_preferred_model_for_task(cat_1)
    print(f"   Updated Preferred Model for '{cat_1}' tasks: {pref_model}")


    print("\n✨ Phase 36 Zero-Cost Local-First LLM Intelligence Gateway Demonstration Complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
