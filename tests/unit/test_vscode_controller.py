"""Unit test for VSCodeController and autonomous code typing in VS Code."""

from unittest.mock import patch
from jarvisx.automation.vscode_controller import VSCodeController
from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator


def test_vscode_controller_create_code_file(tmp_path):
    ctrl = VSCodeController(workspace_dir=str(tmp_path))
    with patch.object(ctrl, "focus_or_launch", return_value=True):
        res = ctrl.create_and_type_code(filename="test_array.py", live_type=False)
        assert res["status"] == "SUCCESS"
        assert res["filename"] == "test_array.py"
        target = tmp_path / "test_array.py"
        assert target.exists()
        content = target.read_text(encoding="utf-8")
        assert "DynamicArray" in content


def test_dynamic_orchestrator_routes_vscode_control():
    orch = DynamicOrchestrator()
    with patch("jarvisx.automation.vscode_controller.VSCodeController.focus_or_launch", return_value=True):
        r1 = orch.execute_voice_command("can u control vs code or not", persona="ALFRED")
        assert r1["action"] == "vscode_control"
        assert "Yes Sir" in r1["response"]

        r2 = orch.execute_voice_command("do it yourself in vs code", persona="ALFRED")
        assert r2["action"] == "vscode_type"
        assert "array_implementation.py" in r2["response"]
