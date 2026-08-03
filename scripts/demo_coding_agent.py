#!/usr/bin/env python3
"""
Live Demonstration Script for Phase 27: Advanced Coding Agent Capability
Simulates a user asking to "Add a calculator API endpoint to this FastAPI project",
traversing the entire pipeline through HermesBus event orchestration.
"""

import asyncio
import json
import tempfile
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.capabilities.coding.coding_adapter import CodingAdapter
from jarvisx.capabilities.permission_manager import PermissionManager, PermissionLevel
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event

async def event_logger(event: Event):
    t = event.type
    p = event.payload
    if t == "coding.task.started":
        print(f"🚀 [HERMES EVENT] Task Started: '{p.get('task')}' in {p.get('repo')}")
    elif t == "coding.plan.created":
        print(f"📋 [HERMES EVENT] Planner Agent generated {len(p.get('steps', []))} steps:")
        for s in p.get('steps', []):
            print(f"   Step {s['step_id']}: [{s['action_type'].upper()}] {s['title']} -> {s.get('target_file')}")
    elif t == "coding.code.modified":
        print(f"⚡ [HERMES EVENT] Developer Agent applied {p.get('changes_count')} code modifications.")
    elif t == "coding.tests.completed":
        status_icon = "✅" if p.get("passed") else "❌"
        print(f"{status_icon} [HERMES EVENT] Tester Agent completed test run: Passed={p.get('passed')}")
    elif t == "coding.review.completed":
        status_icon = "APPROVED" if p.get("approved") else "REJECTED"
        print(f"🔍 [HERMES EVENT] Reviewer Agent score: {p.get('score')} | Status: {status_icon}")

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 70)

    print("      JARVIS X - ADVANCED CODING AGENT CAPABILITY DEMONSTRATION")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as repo_dir:
        repo_path = Path(repo_dir)
        print(f"\n📂 Initializing sample repository at: {repo_path}")

        # Create starter FastAPI files
        main_py = repo_path / "main.py"
        main_py.write_text(
            "from fastapi import FastAPI\n\n"
            "app = FastAPI(title='JarvisX Sample API')\n\n"
            "@app.get('/')\n"
            "def read_root():\n"
            "    return {'status': 'active'}\n",
            encoding="utf-8"
        )

        test_py = repo_path / "test_main.py"
        test_py.write_text(
            "def test_root():\n"
            "    assert True\n",
            encoding="utf-8"
        )

        bus = HermesBus()
        # Subscribe event loggers for multi-agent events
        bus.subscribe("coding.task.started", event_logger)
        bus.subscribe("coding.plan.created", event_logger)
        bus.subscribe("coding.code.modified", event_logger)
        bus.subscribe("coding.tests.completed", event_logger)
        bus.subscribe("coding.review.completed", event_logger)

        pm = PermissionManager()
        pm.request_permission("coding_agent", PermissionLevel.READ)
        pm.request_permission("coding_agent", PermissionLevel.WRITE)
        pm.request_permission("coding_agent", PermissionLevel.EXECUTE)

        adapter = CodingAdapter(bus=bus, permission_manager=pm)
        await adapter.initialize()

        task_prompt = "Add a calculator API endpoint to this FastAPI project"
        print(f"\n💬 User Request: \"{task_prompt}\"")
        print("-" * 70)

        # Prepare code edits to simulate Developer Agent creating calculator endpoint
        calculator_code = (
            "from fastapi import FastAPI, HTTPException\n\n"
            "app = FastAPI(title='JarvisX Sample API')\n\n"
            "@app.get('/')\n"
            "def read_root():\n"
            "    return {'status': 'active'}\n\n"
            "@app.get('/calculator')\n"
            "def calculate(op: str, a: float, b: float):\n"
            "    if op == 'add':\n"
            "        return {'op': op, 'a': a, 'b': b, 'result': a + b}\n"
            "    elif op == 'sub':\n"
            "        return {'op': op, 'a': a, 'b': b, 'result': a - b}\n"
            "    elif op == 'mul':\n"
            "        return {'op': op, 'a': a, 'b': b, 'result': a * b}\n"
            "    elif op == 'div':\n"
            "        if b == 0:\n"
            "            raise HTTPException(status_code=400, detail='Division by zero')\n"
            "        return {'op': op, 'a': a, 'b': b, 'result': a / b}\n"
            "    raise HTTPException(status_code=400, detail='Invalid operator')\n"
        )

        inputs = {
            "repository": str(repo_path),
            "task_description": task_prompt,
            "test_command": "python -c \"import main; print('FastAPI module loaded successfully')\"",
            "code_edits": [
                {
                    "file": "main.py",
                    "content": calculator_code
                }
            ]
        }

        output = await adapter.execute(inputs)

        print("-" * 70)
        print("📊 EXECUTION SUMMARY")
        print("-" * 70)
        print(f"Status:            {output['status']}")
        print(f"Detected Framework:{output['repository_context']['framework']}")
        print(f"Files Modified:    {len(output['code_changes'])}")
        print(f"Review Score:      {output['review']['score']} / 1.0")
        print(f"Review Comments:   {output['review']['comments']}")
        print(f"Metrics:           {json.dumps(output['metrics'], indent=2)}")

        print("\n📝 MODIFIED main.py CODE PREVIEW:")
        print(main_py.read_text(encoding="utf-8"))

        await adapter.shutdown()
        print("\n✨ Demonstration completed successfully!")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
