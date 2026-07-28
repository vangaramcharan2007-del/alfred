"""
Autonomous Learning Loop Demo — Jarvis X
=========================================

Demonstrates the full cognitive learning pipeline:

  FIRST TASK  →  Experience  →  Knowledge Extraction  →  Graph Update
  FEEDBACK    →  Preference Stored
  SECOND TASK →  Alfred retrieves learned context  →  Decision improved
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider
from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.learning.experience_engine import ExperienceEngine
from jarvisx.learning.knowledge_extractor import KnowledgeExtractor
from jarvisx.learning.knowledge_graph import KnowledgeGraph
from jarvisx.learning.learning_engine import LearningEngine
from jarvisx.learning.feedback_engine import FeedbackEngine
from jarvisx.agents.adaptation_manager import AdaptationManager
from jarvisx.core.distributed_scheduler import DistributedScheduler
from jarvisx.agents.capability_registry import CapabilityRegistry
from jarvisx.nodes.node_registry import NodeRegistry


async def main():
    print("\n" + "=" * 60)
    print("   AUTONOMOUS LEARNING LOOP DEMO — JARVIS X")
    print("=" * 60)

    # ── Bootstrap ───────────────────────────────────────────────
    provider = SQLiteMemoryProvider()
    memory = CognitiveMemory(provider)
    graph = KnowledgeGraph()
    exp_engine = ExperienceEngine(memory)
    extractor = KnowledgeExtractor(memory)
    learning = LearningEngine(exp_engine, extractor, graph, memory)
    feedback_engine = FeedbackEngine(memory, graph)
    adaptation = AdaptationManager(memory, graph)
    scheduler = DistributedScheduler(CapabilityRegistry(), NodeRegistry())

    # ── FIRST TASK: "Create a travel video" ─────────────────────
    print("\n--- FIRST TASK ---")
    print('[USER] "Create a travel video"')
    print("[EDITING_AGENT] Completing task...")

    task_result_1 = {
        "type": "creative_task",
        "action": "video_editing",
        "result": "success",
        "agent": "editing_agent",
        "preferences_detected": [],
    }
    result_1 = await learning.learn(task_result_1)
    print(f"-> Experience captured: {result_1['experience']['action']}")
    print(f"-> Entities extracted: {len(result_1['entities'])}")
    print(f"-> Relationships created: {len(result_1['relationships'])}")
    print(f"-> Facts stored: {result_1['facts_stored']}")

    # ── USER FEEDBACK: "Make it more cinematic" ─────────────────
    print("\n--- USER FEEDBACK ---")
    print('[USER] "Make it more cinematic"')

    feedback = await feedback_engine.capture_feedback("I prefer cinematic editing with slow transitions")
    print(f"-> Feedback classified as: {feedback['type']}")
    print(f"-> Confidence: {feedback['confidence']}")

    mem_id = await feedback_engine.update_memory(feedback)
    print(f"-> Stored in memory: {mem_id}")

    # Apply feedback to agent profile
    await adaptation.apply_feedback("editing_agent", feedback)
    await adaptation.update_preferences("editing_agent", "editing_style", "cinematic")
    print("-> Agent profile updated with preference: cinematic editing")

    # ── SECOND TASK: "Create another travel video" ──────────────
    print("\n--- SECOND TASK ---")
    print('[USER] "Create another travel video"')

    # Alfred retrieves learned context
    learned = await learning.apply_learning("editing_agent", "video_editing")
    print(f"-> Learned preferences: {learned['preferences']}")
    print(f"-> Strategies: {learned['strategies']}")

    # Get agent adaptation context
    agent_ctx = adaptation.get_agent_context("editing_agent")
    print(f"-> Agent adaptation score: {agent_ctx['adaptation_score']}")
    print(f"-> Learned behaviors: {agent_ctx['learned_behaviors']}")
    print(f"-> Agent preferences: {agent_ctx['preferences']}")

    # Scheduler uses learned preferences for intelligent node selection
    telemetry = [
        {"node": "node_a", "gpu": "available", "status": "online", "success_rate": 95, "latency": "10ms", "history_score": 0.3},
        {"node": "node_b", "gpu": "available", "status": "online", "success_rate": 70, "latency": "50ms", "history_score": 0.0},
    ]
    best_node = scheduler.select_best_node(
        "editing_agent", ["video_editing"], telemetry,
        user_preferences=learned,
    )
    print(f"-> Scheduler selected: {best_node} (with historical intelligence)")

    # ── KNOWLEDGE GRAPH SNAPSHOT ────────────────────────────────
    print("\n--- KNOWLEDGE GRAPH ---")
    graph_data = graph.to_dict()
    print(f"-> Entities: {graph_data['entity_count']}")
    print(f"-> Relationships: {graph_data['relationship_count']}")
    for rel in graph_data["relationships"][:5]:
        print(f"   {rel['source']} --[{rel['relation']}]--> {rel['target']} (confidence: {rel['confidence']})")

    # ── FINAL SUMMARY ───────────────────────────────────────────
    print("\n" + "=" * 60)
    print("   LEARNING LOOP VERIFICATION")
    print("=" * 60)

    checks = [
        ("Experience captured", result_1["facts_stored"] > 0),
        ("Knowledge extracted", len(result_1["entities"]) > 0),
        ("Relationships created", len(result_1["relationships"]) > 0),
        ("Memory retrieved", mem_id.startswith("mem_")),
        ("Learning applied", len(learned["preferences"]) > 0 or len(learned["strategies"]) > 0),
        ("Agent behavior improved", agent_ctx["adaptation_score"] > 0),
    ]

    all_pass = True
    for label, passed in checks:
        status = "[PASS]" if passed else "[FAIL]"
        if not passed:
            all_pass = False
        print(f"  {status} {label}")

    print()
    if all_pass:
        print("SUCCESS: Autonomous learning loop is fully operational.")
    else:
        print("FAILURE: Some learning checks did not pass.")
        return 1

    print()
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
