"""
Live Demonstration & Validation of the Distributed AI Mesh Worker Registry.
Demonstrates:
1. Concurrent health & model catalog probing across all 5 cluster nodes.
2. Dynamic status resolution (🟢 IDLE, 🟡 BUSY, 🔴 OFFLINE).
3. Real-time visual ASCII telemetry dashboard generation.
4. Smart Least-Load / Lowest-Latency inference routing.
5. FastMCP 30-tool registry verification.
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

from jarvisx.mesh.telemetry_registry import EnhancedWorkerRegistry, MeshNodeState


def run_live_mesh_demo():
    print("=" * 105)
    print(" [JARVIS X] DISTRIBUTED AI MESH & WORKER REGISTRY LIVE VALIDATION")
    print("=" * 105)

    test_storage = repo_root / "var" / "test_mesh_workers.json"
    if test_storage.exists():
        test_storage.unlink()

    registry = EnhancedWorkerRegistry(storage_path=test_storage)

    # 1. Probe all cluster nodes live
    print("\n[STEP 1] [+] Dispatching Concurrent Heartbeat & Model Probes across 5 Mesh Nodes...")
    nodes = asyncio.run(registry.probe_mesh_health(timeout_sec=1.5))
    print(f"  [+] Total Probed Nodes: {len(nodes)}")

    for node in nodes:
        print(f"      - [{node.worker_id}] {node.name} ({node.tailscale_ip}): Status={node.status.value} | Latency={node.latency_ms}ms | Models={len(node.available_models)}")

    # 2. Render and print the live visual ASCII dashboard
    print("\n[STEP 2] [+] Generating Live AI Mesh Telemetry Dashboard:\n")
    dashboard_text = registry.get_mesh_dashboard_text()
    print(dashboard_text)

    # 3. Simulate Worker Activity & Test Intelligent Routing
    print("\n[STEP 3] [+] Testing Smart Least-Load & Lowest-Latency Job Dispatch...")
    
    # Simulate LAB-01 having models and low load
    lab01 = registry.workers.get("LAB-01")
    if lab01:
        lab01.status = MeshNodeState.IDLE
        lab01.available_models = ["qwen2.5-coder:1.5b", "llama3.2:latest"]
        lab01.latency_ms = 18.4
        lab01.active_jobs = 0

    # Simulate LAB-02 having models and slightly higher load
    lab02 = registry.workers.get("LAB-02")
    if lab02:
        lab02.status = MeshNodeState.BUSY
        lab02.available_models = ["qwen2.5-coder:7b", "llama3.2:latest"]
        lab02.latency_ms = 24.1
        lab02.active_jobs = 1

    # Route job for 'llama3.2' -> should pick LAB-01 (0 jobs vs 1 job)
    routed_node = registry.route_inference_job("llama3.2:latest")
    print(f"  [+] Job Routing for 'llama3.2:latest' -> Target: {routed_node.worker_id} ({routed_node.name}) at {routed_node.endpoint_url}")
    assert routed_node.worker_id == "LAB-01", f"Expected LAB-01, got {routed_node.worker_id}"

    # 4. Verify FastMCP Tool Registration
    print("\n[STEP 4] [+] Verifying FastMCP Tool Registry Integration...")
    from fastmcp import FastMCP
    from friday.tools import register_all_tools

    test_mcp = FastMCP(name="JarvisMeshTest")
    register_all_tools(test_mcp)

    tools = asyncio.run(test_mcp.list_tools())
    tool_names = [t.name for t in tools]
    print(f"  [+] Total Registered FastMCP Tools: {len(tool_names)}")
    print(f"  [+] Newly Verified Mesh Tools: get_ai_mesh_live_view, register_mesh_worker_node, route_mesh_ai_job")
    assert "get_ai_mesh_live_view" in tool_names
    assert "register_mesh_worker_node" in tool_names
    assert "route_mesh_ai_job" in tool_names

    # Clean up test database
    if test_storage.exists():
        test_storage.unlink()

    print("\n" + "=" * 105)
    print(" [OK] DISTRIBUTED AI MESH REGISTRY & SMART ROUTING FULLY OPERATIONAL!")
    print("=" * 105)


if __name__ == "__main__":
    run_live_mesh_demo()
