#!/usr/bin/env python3
"""
Live Demonstration Script for Phase 30: Autonomous Software Architect Capability
Demonstrates system architecture design, ADR generation, Mermaid diagram visualization,
and roadmap extraction for a complex AI project idea ("Build a real-time AI meeting assistant").
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.capabilities.coding.architecture_agent import ArchitectureAgent
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event

async def event_logger(event: Event):
    t = event.type
    p = event.payload
    if t == "coding.architect.started":
        print(f"🚀 [HERMES EVENT] Software Architect Mission Started: '{p.get('idea')}'")
    elif t == "coding.architect.proposed":
        print(f"📐 [HERMES EVENT] Proposed System Architecture '{p.get('project_name')}' with {p.get('components_count')} components.")
    elif t == "coding.architect.adr_created":
        print(f"📝 [HERMES EVENT] Created {p.get('decision_id')}: '{p.get('title')}' ({p.get('status')})")

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("      JARVIS X - PHASE 30 AUTONOMOUS SOFTWARE ARCHITECT DEMO")
    print("=" * 80)

    user_idea = "Build a real-time AI meeting assistant"
    print(f"\n💡 User Project Request: \"{user_idea}\"")
    print("-" * 80)

    bus = HermesBus()
    bus.subscribe("coding.architect.started", event_logger)
    bus.subscribe("coding.architect.proposed", event_logger)
    bus.subscribe("coding.architect.adr_created", event_logger)

    agent = ArchitectureAgent(bus=bus)

    print("\n🤖 Generating Software Architecture Proposal...")
    print("-" * 80)

    result = await agent.design_system(
        idea_description=user_idea,
        constraints={
            "backend": "FastAPI (Python 3.11)",
            "frontend": "Next.js 14 + React",
            "database": "PostgreSQL + Redis"
        }
    )

    print("-" * 80)
    print(f"🏗️  PROJECT ARCHITECTURE: {result['project_name']}")
    print("-" * 80)

    tech = result["architecture"]["technology_stack"]
    print("💻 Technology Stack:")
    for layer, choice in tech.items():
        print(f"   - {layer.capitalize():<15}: {choice}")

    print("\n🧱 Components Breakdown:")
    for comp in result["architecture"]["components"]:
        deps_str = ", ".join(comp["dependencies"]) if comp["dependencies"] else "None"
        print(f"   - [{comp['name']}]")
        print(f"     Responsibility: {comp['responsibility']}")
        print(f"     Dependencies:   {deps_str}")

    print("\n📝 Architecture Decision Records (ADRs):")
    for adr in result["adrs"]:
        print(f"   - [{adr['decision_id']}] {adr['title']}")
        print(f"     Reasoning:    {adr['reasoning']}")
        print(f"     Tradeoffs:    {', '.join(adr['consequences'])}")

    print("\n📊 MERMAID COMPONENT DIAGRAM:")
    print(result["diagrams"]["component_diagram"])

    print("\n📊 MERMAID DATA FLOW DIAGRAM:")
    print(result["diagrams"]["data_flow_diagram"])

    print("\n🗺️  ACTIONABLE IMPLEMENTATION ROADMAP:")
    for step in result["roadmap"]:
        print(f"   {step}")

    print("\n✨ Phase 30 Autonomous Software Architect Demonstration Complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
