"""
Live Demonstration & Validation of the 13-Specialist Agent Fleet for Jarvis X.
Demonstrates:
1. Fleet Metadata & Specialist Skill Verification (gstack workflows preserved).
2. Multi-Agent Orchestration & Mesh Job Routing (Alfred -> Architect -> Security -> QA -> Release).
3. Cryptographic Audit Ledger Integration for every dispatched agent turn.
4. FastMCP 32-Tool Registry Integration.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(repo_root / "friday-tony-stark-demo"))

from jarvisx.agents.fleet_manager import AgentRole, get_agent_fleet_manager
from jarvisx.security.audit_ledger import CryptographicAuditLedger


def run_live_fleet_demo():
    print("=" * 105)
    print(" [JARVIS X] 13-SPECIALIST AGENT FLEET & DISTRIBUTED MESH LIVE VALIDATION")
    print("=" * 105)

    fleet = get_agent_fleet_manager()
    agents = fleet.list_fleet()

    # 1. Verify 13 Specialist Agents and their preserved gstack SKILL.md workflows
    print(f"\n[STEP 1] [+] Inspecting {len(agents)} Registered Specialist Agents in Fleet:\n")
    print(f"{'ROLE':<22} {'NAME':<28} {'MODEL FAMILY':<20} {'GSTACK SKILL WORKFLOW'}")
    print("-" * 105)

    for a in agents:
        skill_str = a["skill_workflow"] if a["skill_workflow"] else "(Direct FastMCP Agent)"
        print(f"{a['role']:<22} {a['name']:<28} {a['preferred_model']:<20} {skill_str}")
        if a["skill_workflow"]:
            skill_p = repo_root / a["skill_workflow"]
            assert skill_p.exists(), f"Missing preserved skill workflow: {skill_p}"

    assert len(agents) == 13, f"Expected 13 agents, found {len(agents)}"

    # 2. Multi-Agent Pipeline Execution: Alfred -> Architect -> Security -> QA -> Release
    print("\n[STEP 2] [+] Executing Distributed Multi-Agent Pipeline across Tailscale Mesh...")

    pipeline_steps = [
        (AgentRole.ALFRED_PLANNER, "Decompose the user mission to integrate a real-time microgrid telemetry stream into HUD."),
        (AgentRole.ARCHITECT_AGENT, "Define modular FastMCP schema contracts and zero-hardcoding IPC interfaces."),
        (AgentRole.SECURITY_AGENT, "Verify permission scope boundaries (CONFIRM required for relay actuation, read-only telemetry)."),
        (AgentRole.QA_AGENT, "Execute unit acceptance tests and verify zero exceptions on empty socket streams."),
        (AgentRole.RELEASE_AGENT, "Execute pre-flight checks, format changelog, and stamp cryptographic audit ledger."),
    ]

    for role, prompt in pipeline_steps:
        exec_res = fleet.dispatch_agent_task(role, prompt)
        print(f"  [+] [{exec_res.role.value.upper()}] Dispatched to {exec_res.target_worker} ({exec_res.worker_url}) in {exec_res.duration_ms}ms")
        print(f"      - Audit Hash: {exec_res.audit_hash[:16]}... | Status: {exec_res.status}")
        assert exec_res.status == "COMPLETED"

    # 3. Verify Cryptographic Audit Chain Integrity
    print("\n[STEP 3] [+] Verifying Tamper-Evident Cryptographic Audit Chain for Dispatched Turns...")
    integrity = fleet.audit_ledger.verify_integrity()
    print(f"  [+] Audit Chain Integrity: {integrity['status']} (Total Audited Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    # 4. Verify FastMCP Tool Registry Integration
    print("\n[STEP 4] [+] Verifying FastMCP Tool Registry Integration...")
    from fastmcp import FastMCP
    from friday.tools import register_all_tools

    test_mcp = FastMCP(name="JarvisFleetTest")
    register_all_tools(test_mcp)

    tools = asyncio.run(test_mcp.list_tools())
    tool_names = [t.name for t in tools]
    print(f"  [+] Total Registered FastMCP Tools: {len(tool_names)}")
    print(f"  [+] Verified Fleet Tools: list_jarvis_agent_fleet, dispatch_specialist_agent, execute_ship_gate")
    assert "list_jarvis_agent_fleet" in tool_names
    assert "dispatch_specialist_agent" in tool_names
    assert "execute_ship_gate" in tool_names

    print("\n" + "=" * 105)
    print(" [OK] 13-SPECIALIST AGENT FLEET & DISTRIBUTED MESH FULLY OPERATIONAL!")
    print("=" * 105)


if __name__ == "__main__":
    run_live_fleet_demo()
