#!/usr/bin/env python3
"""
Live Demonstration Script for Phase 35: Real OpenHands Engineering Integration
Demonstrates OpenHands discovery, registration, workspace creation, repository loading,
mission planning, feature implementation, progress streaming, testing, review, GitHub integration,
workspace cleanup, and fallback handling when OpenHands is unavailable.
"""

import asyncio
import json
import tempfile
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.openhands.openhands_adapter import OpenHandsCapabilityAdapter
from jarvisx.capabilities.github.github_capability import GitHubCapability

async def event_logger(event: Event):
    t = event.type
    p = event.payload
    if t == "openhands.connected":
        print(f"🔌 [HERMES EVENT] OpenHands Engineering Runtime Connected (Runtime Available: {p.get('runtime_available')})")
    elif t == "openhands.workspace.created":
        print(f"📂 [HERMES EVENT] OpenHands Workspace Created: '{p.get('workspace_id')}' at {p.get('path')}")
    elif t == "openhands.task.started":
        print(f"⚙️  [HERMES EVENT] OpenHands Task Started: '{p.get('mission')}'")
    elif t == "openhands.task.progress":
        print(f"⏳ [HERMES EVENT] OpenHands Progress: {p.get('progress')}% (Sandbox: {p.get('sandbox_id')})")
    elif t == "openhands.task.completed":
        print(f"✅ [HERMES EVENT] OpenHands Task Completed: '{p.get('mission')}' in {p.get('duration')}s")

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("      JARVIS X - PHASE 35 OPENHANDS ENGINEERING RUNTIME INTEGRATION DEMO")
    print("=" * 80)

    bus = HermesBus()
    bus.subscribe("openhands.connected", event_logger)
    bus.subscribe("openhands.workspace.created", event_logger)
    bus.subscribe("openhands.task.started", event_logger)
    bus.subscribe("openhands.task.progress", event_logger)
    bus.subscribe("openhands.task.completed", event_logger)

    registry = CapabilityRegistry(bus=bus)
    oh_adapter = OpenHandsCapabilityAdapter(bus=bus)
    await oh_adapter.register(registry)

    github_cap = GitHubCapability(bus=bus)
    await github_cap.register_capability(registry)

    print("\n🔍 Step 1: OpenHands Provider Discovery & Health Check...")
    health = await oh_adapter.provider.health()
    print(f"   Provider Name:     {oh_adapter.provider.metadata()['name']}")
    print(f"   Health Status:     {health['status']}")
    print(f"   Runtime Available: {health['runtime_available']}")

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        (repo_path / "app.py").write_text("def run(): pass\n", encoding="utf-8")

        print(f"\n📂 Step 2: Creating Workspace & Opening Repository at {repo_path}")
        ws_res = await registry.execute("openhands.workspace", "open_repository", repo_path=str(repo_path))
        ws_info = ws_res["workspace"]
        print(f"   Workspace ID:      {ws_info['workspace_id']}")
        print(f"   Workspace Path:    {ws_info['path']}")

        print("\n📌 Step 3: Executing OpenHands Mission ('implement_feature')...")
        task_desc = "Add Redis Caching layer for fast query response"
        oh_result = await registry.execute(
            "openhands.engineering",
            "implement_feature",
            task_description=task_desc,
            repo_path=str(repo_path),
            session_id="oh_sess_demo"
        )
        print(f"   Execution Status:  {oh_result['status']}")
        print(f"   Architecture Plan: {oh_result['architecture_plan']}")
        print(f"   Sandbox Container: {oh_result['mission']['sandbox_id']}")

        print("\n🛡️  Step 4: Code Review & Risk Assessment...")
        changes = [{"file_path": "cache_service.py", "action": "created", "content_after": "import redis\n"}]
        review = await registry.execute("openhands.review", "assess_risk", file_changes=changes)
        print(f"   Risk Assessment Level: {review['risk_assessment']['risk_level']}")

        print("\n📝 Step 5: Creating GitHub Issue & Pull Request...")
        issue = await registry.execute(
            "github.engineering",
            "create_issue",
            title="Implement Redis Caching Layer",
            body=task_desc
        )
        pr = await registry.execute(
            "github.engineering",
            "create_pr",
            title=f"feat(cache): {issue['title']} (Closes #{issue['number']})",
            body="Added Redis caching layer via OpenHands Engineering Runtime.",
            head_branch="openhands/redis-cache",
            base_branch="main"
        )
        print(f"   GitHub PR #{pr['number']} Created: '{pr['title']}'")

        print("\n🧹 Step 6: Cleaning Up Workspace...")
        cleanup_res = await registry.execute("openhands.workspace", "close_workspace", workspace_id=ws_info['workspace_id'])
        print(f"   Workspace Closed:  {cleanup_res['success']}")

    print("\n✨ Phase 35 Real OpenHands Engineering Integration Demonstration Complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
