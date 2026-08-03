import pytest
import tempfile
from pathlib import Path
from jarvisx.capabilities.permission_manager import PermissionManager, PermissionLevel
from jarvisx.capabilities.coding.autonomous_loop import AutonomousLoop

@pytest.mark.asyncio
async def test_autonomous_loop_successful_repair():
    pm = PermissionManager()
    pm.request_permission("coding_agent", PermissionLevel.READ)
    pm.request_permission("coding_agent", PermissionLevel.WRITE)
    pm.request_permission("coding_agent", PermissionLevel.EXECUTE)

    loop = AutonomousLoop(max_attempts=3, permission_manager=pm)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a buggy file with intentional ZeroDivisionError
        buggy_code = (
            "def calculate(op, a, b):\n"
            "    if op == 'div':\n"
            "        return a / b\n"
            "    return a + b\n"
        )
        
        test_code = (
            "import main\n"
            "try:\n"
            "    main.calculate('div', 10, 0)\n"
            "except Exception:\n"
            "    print('Handled zero division cleanly')\n"
        )
        
        Path(tmpdir, "test_main.py").write_text(test_code, encoding="utf-8")

        inputs_edits = [{"file": "main.py", "content": buggy_code}]

        report = await loop.run(
            repo_path=tmpdir,
            task_description="Fix calculator zero division bug",
            test_command="python test_main.py",
            initial_code_edits=inputs_edits
        )

        assert report.status in ["repaired_and_passed", "success"]
        assert report.total_attempts >= 1
        assert report.metrics["coding_tasks_completed"] >= 1

@pytest.mark.asyncio
async def test_autonomous_loop_max_retries_limit():
    pm = PermissionManager()
    pm.request_permission("coding_agent", PermissionLevel.READ)
    pm.request_permission("coding_agent", PermissionLevel.WRITE)
    pm.request_permission("coding_agent", PermissionLevel.EXECUTE)

    loop = AutonomousLoop(max_attempts=2, permission_manager=pm)

    with tempfile.TemporaryDirectory() as tmpdir:
        report = await loop.run(
            repo_path=tmpdir,
            task_description="Run failing test",
            test_command="python -c \"import sys; sys.exit(1)\""
        )

        assert report.status == "failed_max_retries"
        assert report.total_attempts == 2
