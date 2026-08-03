import pytest
import tempfile
from pathlib import Path
from jarvisx.capabilities.permission_manager import PermissionManager, PermissionLevel
from jarvisx.capabilities.coding.error_analyzer import DebuggingContext
from jarvisx.capabilities.coding.pipeline.code_executor import CodeExecutor
from jarvisx.capabilities.coding.repair_planner import RepairPlanner

def test_repair_planner_zero_division():
    planner = RepairPlanner()
    pm = PermissionManager()
    pm.request_permission("coding_agent", PermissionLevel.WRITE)
    executor = CodeExecutor(permission_manager=pm)

    with tempfile.TemporaryDirectory() as tmpdir:
        main_py = Path(tmpdir) / "main.py"
        main_py.write_text("def calculate(a, b):\n    return a / b\n", encoding="utf-8")

        debug_ctx = DebuggingContext(
            exception_type="ZeroDivisionError",
            error_message="division by zero",
            failing_file="main.py",
            line_number=2,
            likely_root_cause="Division by zero without zero guard check"
        )

        plan = planner.create_repair_plan(tmpdir, debug_ctx)
        assert plan.target_file == "main.py"
        assert "zero" in plan.proposed_fix_description.lower()

        change_rec = planner.apply_repair_plan(tmpdir, plan, executor)
        assert change_rec.file_path == "main.py"
        assert (Path(tmpdir) / "main.py").read_text() != "def calculate(a, b):\n    return a / b\n"
