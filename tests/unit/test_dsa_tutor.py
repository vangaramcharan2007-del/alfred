"""Unit tests for DSATutorEngine in Jarvis X."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from jarvisx.tutor.dsa_tutor import DSATutorEngine, CURRICULUM_ROADMAP
from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator


def test_curriculum_roadmap_integrity():
    assert len(CURRICULUM_ROADMAP) >= 5
    for item in CURRICULUM_ROADMAP:
        assert "day" in item
        assert "topic" in item
        assert "code" in item
        assert "video_url" in item
        assert len(item["code"]) > 50


def test_dsa_tutor_launch_lesson(tmp_path):
    tutor = DSATutorEngine(workspace_root=str(tmp_path))
    with patch("webbrowser.open") as mock_web, \
         patch.object(tutor.vscode, "focus_or_launch", return_value=True):
        
        res = tutor.launch_daily_lesson(day=1, open_video=True, open_vscode=True)
        assert res["status"] == "SUCCESS"
        assert res["day"] == 1
        assert "Arrays" in res["topic"]
        assert mock_web.called

        # Check created file
        dsa_file = tmp_path / res["filename"]
        assert dsa_file.exists()
        content = dsa_file.read_text(encoding="utf-8")
        assert "two_sum" in content


def test_dynamic_orchestrator_dsa_intent(tmp_path):
    orch = DynamicOrchestrator()
    with patch("webbrowser.open"), \
         patch("jarvisx.automation.vscode_controller.VSCodeController.focus_or_launch", return_value=True):
        
        res = orch._execute_single_voice_command("teach me dsa")
        assert res["action"] == "dsa_tutor"
        assert "Data Structures and Algorithms" in res["response"]
        assert "Arrays" in res["response"]
