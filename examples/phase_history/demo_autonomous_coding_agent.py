#!/usr/bin/env python3
"""
Live Demonstration Script for Phase 28: Autonomous Coding Loop + Self-Debugging Capability
Simulates an intentional bug scenario, where the agent automatically detects a failure,
analyzes the traceback, generates a repair plan, applies the fix, re-tests, and reports success.
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
        print(f"🚀 [HERMES EVENT] Autonomous Mission Started: '{p.get('task')}'")
    elif t == "coding.tests.completed":
        status_icon = "✅ PASSED" if p.get("passed") else "❌ FAILED"
        print(f"🧪 [HERMES EVENT] Test Run Attempt {p.get('attempt')}: {status_icon}")
    elif t == "coding.repair.started":
        ctx = p.get("debugging_context", {})
        print(f"🔍 [HERMES EVENT] Error Analyzer Detected: {ctx.get('exception_type')} in {ctx.get('failing_file')}:{ctx.get('line_number')}")
        print(f"💡 Root Cause: {ctx.get('likely_root_cause')}")
    elif t == "coding.repair.applied":
        plan = p.get("repair_plan", {})
        print(f"🔧 [HERMES EVENT] Repair Planner Applied Fix: '{plan.get('proposed_fix_description')}' to {plan.get('target_file')}")
    elif t == "coding.repair.passed":
        print(f"🎉 [HERMES EVENT] Self-Debugging Loop Successfully Resolved Bug in Attempt {p.get('attempts')}!")

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 75)
    print("   JARVIS X - PHASE 28 AUTONOMOUS CODING & SELF-DEBUGGING DEMO")
    print("=" * 75)

    with tempfile.TemporaryDirectory() as repo_dir:
        repo_path = Path(repo_dir)
        print(f"\n📂 Initializing test workspace at: {repo_path}")

        # Step 1: Inject intentional bug into main.py (division by zero)
        buggy_main_py = (
            "from fastapi import FastAPI\n\n"
            "app = FastAPI(title='JarvisX Buggy API')\n\n"
            "@app.get('/calculator')\n"
            "def calculate(a: float, b: float):\n"
            "    # INTENTIONAL BUG: No zero check before division!\n"
            "    return {'result': a / b}\n"
        )
        main_file = repo_path / "main.py"
        main_file.write_text(buggy_main_py, encoding="utf-8")

        # Create test script that triggers division by zero
        test_script = (
            "import sys, os\n"
            "sys.path.insert(0, os.getcwd())\n"
            "from main import calculate\n\n"
            "try:\n"
            "    print('Testing normal division: 10 / 2 ->', calculate(10, 2))\n"
            "    print('Testing edge case: 10 / 0')\n"
            "    res = calculate(10, 0)\n"
            "    sys.exit(0)\n"
            "except Exception as e:\n"
            "    if isinstance(e, ZeroDivisionError):\n"
            "        print('ZeroDivisionError crash!', file=sys.stderr)\n"
            "        raise e\n"
            "    print('Zero division safely caught with error:', e)\n"
            "    sys.exit(0)\n"
        )


        test_file = repo_path / "test_calculator.py"
        test_file.write_text(test_script, encoding="utf-8")

        print("⚠️  Intentional Bug Injected: `calculate(10, 0)` raises `ZeroDivisionError`")

        bus = HermesBus()
        bus.subscribe("coding.task.started", event_logger)
        bus.subscribe("coding.tests.completed", event_logger)
        bus.subscribe("coding.repair.started", event_logger)
        bus.subscribe("coding.repair.applied", event_logger)
        bus.subscribe("coding.repair.passed", event_logger)

        pm = PermissionManager()
        pm.request_permission("coding_agent", PermissionLevel.READ)
        pm.request_permission("coding_agent", PermissionLevel.WRITE)
        pm.request_permission("coding_agent", PermissionLevel.EXECUTE)

        adapter = CodingAdapter(bus=bus, permission_manager=pm)
        await adapter.initialize()

        print("\n🤖 Initiating Autonomous Self-Debugging Cycle...")
        print("-" * 75)

        inputs = {
            "repository": str(repo_path),
            "task_description": "Fix ZeroDivisionError in calculator endpoint",
            "test_command": "python test_calculator.py",
            "initial_code_edits": [
                {"file": "main.py", "content": buggy_main_py}
            ],
            "max_attempts": 3
        }


        output = await adapter.execute(inputs)

        print("-" * 75)
        print("📊 AUTONOMOUS REPAIR SUMMARY")
        print("-" * 75)
        print(f"Final Loop Status:    {output['status']}")
        print(f"Total Attempts Used:  {output['history']['total_attempts']} / 3")
        print(f"Test Execution Passed:{output['test_results']['passed']}")
        print(f"Code Review Score:    {output['review']['score']} / 1.0")
        print(f"Auto-Repairs Metric:  {output['metrics']['auto_repairs_succeeded']} succeeded")

        print("\n📝 REPAIRED main.py CODE PREVIEW:")
        print(main_file.read_text(encoding="utf-8"))

        await adapter.shutdown()
        print("\n✨ Phase 28 Autonomous Self-Debugging Demonstration Complete!")
        print("=" * 75)

if __name__ == "__main__":
    asyncio.run(main())
