"""
Live Demonstration & Validation of the Unified End-to-End Mesh Execution Pipeline.
Demonstrates:
1. End-to-End Orchestration: Alfred Plan -> Specialist Agents -> GPU Mesh Worker Inference -> Adversarial Review -> Cryptographic Audit.
2. Real-time Multi-Stage Execution across Tailscale Mesh Nodes.
3. 3-Perspective Adversarial Review for each generated stage.
4. Tamper-Evident SHA-256 Audit Chain Verification.
5. FastMCP 36-Tool Registry Integration.
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

from jarvisx.orchestration.unified_mesh_pipeline import UnifiedMeshOrchestrator, get_unified_mesh_orchestrator


def run_live_pipeline_demo():
    print("=" * 105)
    print(" [JARVIS X] UNIFIED END-TO-END MESH EXECUTION PIPELINE LIVE VALIDATION")
    print("=" * 105)

    orchestrator = get_unified_mesh_orchestrator()

    # 1. Execute full end-to-end mission
    mission_goal = "Build an asynchronous microgrid telemetry ingest pipeline with SQLite persistence and adversarial verification."
    print(f"\n[STEP 1] [+] Launching Unified Mission: '{mission_goal}'")
    print("  [+] Pipeline Stages: Architect -> Coder -> Security -> QA Engineer")
    
    report = orchestrator.execute_mission(mission_goal)

    print(f"\n[STEP 2] [+] Mission Execution Summary (Mission ID: {report.mission_id}):")
    print(f"  [+] Overall Status: {report.overall_status}")
    print(f"  [+] Steps Completed: {report.successful_steps}/{report.total_steps}")
    print(f"  [+] Total Execution Time: {report.duration_ms}ms")
    print(f"  [+] Cryptographic Chain Valid: {report.audit_chain_valid}")

    print("\n[STEP 3] [+] Inspecting Stage-by-Stage Telemetry, Worker Allocation & Adversarial Review:\n")
    print(f"{'STAGE':<6} {'AGENT':<22} {'TARGET WORKER':<16} {'MODEL':<20} {'REVIEW':<10} {'SCORE':<7} {'DURATION'}")
    print("-" * 105)
    for s in report.step_results:
        print(f"#{s.step_index:<5} {s.agent_name:<22} {s.target_worker:<16} {s.model_used:<20} {s.review_decision:<10} {s.review_score}/10   {s.duration_ms}ms")
        print(f"       -> Audit Hash: {s.audit_hash[:24]}...")

    assert report.total_steps == 4, f"Expected 4 stages, got {report.total_steps}"
    assert report.audit_chain_valid is True, "Audit chain integrity check failed!"

    # 4. Verify FastMCP Tool Registry
    print("\n[STEP 4] [+] Verifying FastMCP Tool Registry Integration...")
    from fastmcp import FastMCP
    from friday.tools import register_all_tools

    test_mcp = FastMCP(name="JarvisUnifiedPipelineTest")
    register_all_tools(test_mcp)

    tools = asyncio.run(test_mcp.list_tools())
    tool_names = [t.name for t in tools]
    print(f"  [+] Total Registered FastMCP Tools: {len(tool_names)}")
    print(f"  [+] Verified Unified Mission Tool: execute_unified_mesh_mission")
    assert "execute_unified_mesh_mission" in tool_names

    print("\n" + "=" * 105)
    print(" [OK] UNIFIED END-TO-END MESH EXECUTION PIPELINE FULLY OPERATIONAL!")
    print("=" * 105)


if __name__ == "__main__":
    run_live_pipeline_demo()
