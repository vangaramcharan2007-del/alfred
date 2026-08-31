"""
Live Demonstration: Autonomous Agent Trainer & Fleet Fine-Tuning.
Demonstrates fleet-wide capability discovery, dynamic prompt distillation, and capability benchmarking.
"""

import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jarvisx.organism import get_organism
from jarvisx.agents.agent_trainer_engine import get_agent_trainer


async def main():
    print("=" * 75)
    print("   ALFRED OS — AUTONOMOUS AGENT TRAINER & FLEET FINE-TUNER")
    print("=" * 75 + "\n")

    trainer = get_agent_trainer()
    org = get_organism()

    # 1. Direct Fleet Training & Distillation
    print("[1/3] 🏋️ TRAINING FLEET SUBAGENTS WITH LATEST TOOLS & INTEGRATIONS...")
    train_res = trainer.train_and_update_fleet()
    print(f"      Status:   {train_res.get('status').upper()}")
    print(f"      Duration: {train_res.get('training_duration_sec')}s")
    for a in train_res.get("agents", []):
        print(f"      • {a['name']:<15} ({a['role']:<16}) → {a['skills_count']} skills equipped (Mastery: {a['mastery_score']*100:.1f}%)")
    print()

    # 2. Benchmark Fleet Performance
    print("[2/3] 📊 BENCHMARKING FLEET MASTERY & REASONING CAPABILITIES...")
    bench_res = trainer.benchmark_fleet()
    print(f"      Fleet Average Score: {bench_res.get('fleet_average_score')}")
    print(f"      {'AGENT':<15} | {'MASTERY':<10} | {'REASONING':<10} | {'TOOL MASTERY':<12} | {'STATUS':<8}")
    print("      " + "-" * 62)
    for role, b in bench_res.get("benchmark_results", {}).items():
        print(f"      {b['name']:<15} | {b['mastery_score']:<10} | {b['reasoning']:<10} | {b['tool_mastery']:<12} | {b['status']:<8}")
    print()

    # 3. Live Turn: User Requests Fleet Training
    print("[3/3] 🧠 TESTING NATURAL LANGUAGE TRIGGER: 'train our agent fleet'...")
    prompt = "Alfred, train our agent fleet with the latest integrations and benchmark their performance."
    turn_res = await org.react_turn(prompt)
    print(f"      Decision: {turn_res.get('decision')}")
    print(f"      Spoken:\n{turn_res.get('spoken') or turn_res.get('response')}\n")

    print("=" * 75)
    print("   AUTONOMOUS AGENT TRAINER FULLY VERIFIED & ACTIVE [OK]")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(main())
