#!/usr/bin/env python3
"""
Jarvis X Unified Autonomous Operating System Layer - Full Runtime Demo
Phase 39 Live Demonstration Script

Demonstrates:
- Kernel boot & Subsystem manager initialization
- Subsystem health verification across all 17 components
- Intent Understanding & Mission Routing
- Unified Decision Engine reasoning (Task, Capability, Provider, Model, Reasons, Risk)
- Autonomous Mission Execution (Architecture Agent -> Planner -> Provider -> Sandbox -> GitHub PR -> Evolution Memory)
- System Knowledge Graph tracking
- Voice Runtime Engine waveform output
- Jarvis CLI status & command handling
"""

import sys
import os
import time
import asyncio
import json

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Ensure src directory is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from jarvisx.kernel.runtime_kernel import RuntimeKernel
from jarvisx.brain.brain_controller import BrainController
from jarvisx.missions.mission_manager import MissionManager
from jarvisx.decision.unified_decision_engine import UnifiedDecisionEngine, DecisionContext
from jarvisx.meta.system_graph import SystemKnowledgeGraph
from jarvisx.interface.cli import JarvisCLI
from jarvisx.interface.voice_runtime import VoiceRuntimeEngine
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.core.hermes import HermesBus

async def run_demo():
    print("=" * 80)
    print("      JARVIS X UNIFIED AUTONOMOUS OPERATING SYSTEM LAYER - PHASE 39")
    print("=" * 80)
    print()

    # 1. Initialize Core Foundations
    registry = CapabilityRegistry()
    bus = HermesBus()
    kernel = RuntimeKernel(registry=registry, bus=bus)
    voice = VoiceRuntimeEngine(bus=bus)
    graph = SystemKnowledgeGraph()

    # Register graph entities
    graph.add_capability("cap.coding", "Coding Agent Capability", {"version": "1.0.0"})
    graph.add_agent("agent.architecture", "Architecture Agent", {"tier": "system"})
    graph.add_model("model.qwen_local", "Qwen2.5-Coder local", {"offline": True, "score": 0.97})
    graph.add_repository("repo.jarvisx", "vangaramcharan2007-del/alfred", {"branch": "main"})
    graph.add_memory("mem.cognitive", "Cognitive Vector Memory", {"size": "42 MB"})

    # 2. Boot Kernel
    print("[STEP 1] Booting Jarvis X Runtime Kernel...")
    boot_info = await kernel.boot()
    print(f"   [+] State: {boot_info['state']}")
    print(f"   [+] Subsystems Online: {boot_info['subsystems_online']} / 17")
    print(f"   [+] Boot Duration: {boot_info['boot_duration']} seconds")
    print()

    # 3. Health Check
    print("[STEP 2] Running Subsystem Health Check...")
    health = kernel.health_check()
    print(f"   [+] Health Score: {health['health_score'] * 100:.1f}%")
    print(f"   [+] Overall Status: {health['overall']}")
    for sub in health['subsystems'][:6]:
        print(f"     - Subsystem [{sub['name']}]: {sub['status']}")
    print(f"     - ... ({len(health['subsystems']) - 6} more subsystems online)")
    print()

    # 4. User Request Input
    user_request = "Create a productivity app"
    print(f"[STEP 3] User Request Received: \"{user_request}\"")
    print()

    # 5. Intent Understanding & Brain Routing
    print("[STEP 4] Jarvis Brain Intent Understanding & Routing...")
    brain = BrainController(registry=registry, bus=bus)
    brain_res = await brain.process_request(user_request)
    print(f"   [+] Detected Intent: {brain_res['intent']['intent']} (Confidence: {brain_res['intent']['confidence']*100:.0f}%)")
    print(f"   [+] Capability Selected: {brain_res['capability']}")
    print(f"   [+] Preferred Provider: {brain_res['provider']}")
    print()

    # 6. Unified Decision Engine
    print("[STEP 5] Unified Decision Engine (Reasoning & Model Selection)...")
    decision_engine = UnifiedDecisionEngine(registry=registry)
    ctx = DecisionContext(task_description=user_request, intent=brain_res['intent']['intent'])
    decision = decision_engine.decide(ctx)
    explanation = decision_engine.explainer.explain(decision)

    print("-" * 50)
    print(explanation)
    print("-" * 50)
    print()

    # Update Graph with Mission & Decision
    graph.add_mission("mission_001", user_request, {"intent": brain_res['intent']['intent']})
    graph.add_edge("mission_001", "model.qwen_local", "uses")
    graph.add_edge("mission_001", "cap.coding", "executes")

    # 7. Execute Autonomous Mission
    print("[STEP 6] Executing Autonomous Mission Pipeline...")
    mission_mgr = MissionManager(brain=brain, registry=registry, bus=bus)
    mission_res = await mission_mgr.create_and_execute_mission(user_request)

    m = mission_res["mission"]
    res = mission_res["result"]

    print(f"   [+] Mission ID: {m['mission_id']}")
    print(f"   [+] Status: {m['status']}")
    print(f"   [+] Architecture Design: {res['architecture']}")
    print(f"   [+] Provider Output: {res['provider_output']['output']}")
    print(f"   [+] Sandbox Test Result: {res['test_result']['stdout']} (Exit code: {res['test_result']['exit_code']})")
    print(f"   [+] GitHub PR Created: #{res['github_pr']['pr_number']} - {res['github_pr']['title']} ({res['github_pr']['url']})")
    print(f"   [+] Review Status: {res['github_pr']['review_status']}")
    print(f"   [+] Recorded Evolution Memory: {res['evolution_memory']['upgrade_id']} (Lessons: {res['evolution_memory']['lessons_learned']})")
    print()

    # 8. Voice Synthesis Output
    print("[STEP 7] Voice Runtime Engine Speech Output...")
    voice_res = voice.speak("Autonomous productivity app mission completed successfully. Pull request is ready for review.", persona="Friday")
    print(f"   [+] Persona: {voice_res['persona']}")
    print(f"   [+] Status: {voice_res['status']}")
    print(f"   [+] Waveform Samples: {voice_res['waveform_samples']}")
    print()

    # 9. CLI Status Verification
    print("[STEP 8] Jarvis CLI Interface Status Check...")
    cli = JarvisCLI(kernel=kernel, mission_manager=mission_mgr)
    cli_status = cli.handle_command("status")
    print(f"   [+] System Health: {cli_status['system_health']}")
    print(f"   [+] Active Agents: {', '.join(cli_status['active_agents'])}")
    print(f"   [+] Available Models: {', '.join(cli_status['models_available'])}")
    print(f"   [+] Memory Size: {cli_status['memory_size']}")
    print(f"   [+] Evolution Level: {cli_status['evolution_level']}")
    print()

    # 10. Global Knowledge Graph Summary
    print("[STEP 9] Global Knowledge Graph Summary...")
    graph_summary = graph.to_dict()
    print(f"   [+] Total Nodes: {graph_summary['nodes_count']}")
    print(f"   [+] Total Edges: {graph_summary['edges_count']}")
    print(f"   [+] Entity Type Summary: {json.dumps(graph_summary['type_summary'])}")
    print()

    print("=" * 80)
    print("  [SUCCESS] PHASE 39: UNIFIED AUTONOMOUS OPERATING SYSTEM DEMO COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_demo())
