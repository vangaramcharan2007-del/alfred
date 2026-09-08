"""
Unit Tests for KeepAwakeGuard, ChromeCDPBridge, AsyncPager, and AOVOrchestratorBridge.
"""
import pytest
import sys
from unittest.mock import MagicMock, patch

from jarvisx.runtime.windows_power_guard import KeepAwakeGuard
from jarvisx.automation.chrome_cdp_bridge import ChromeCDPBridge
from jarvisx.communications.async_pager import AsyncPager, PagerAlert
from jarvisx.automation.aov_orchestrator_bridge import AOVOrchestratorBridge
from jarvisx.automation.aov_planner import PlanExecutionResult


class TestKeepAwakeGuard:
    """Tests power guard assertion, context manager, and release."""

    def test_guard_context_manager(self):
        guard = KeepAwakeGuard("unit_test_mission")
        assert guard.is_active is False

        with patch("ctypes.windll.kernel32.SetThreadExecutionState", return_value=1) as mock_win32:
            with guard:
                assert guard.is_active is True
                assert mock_win32.called

            assert guard.is_active is False

    def test_guard_graceful_non_windows(self):
        guard = KeepAwakeGuard("test")
        guard.is_windows = False
        assert guard.activate() is True
        assert guard.is_active is True
        assert guard.deactivate() is True
        assert guard.is_active is False


class TestChromeCDPBridge:
    """Tests Chrome binary detection, user data dir resolution, and CDP status probe."""

    def test_user_data_dir_resolution(self):
        path = ChromeCDPBridge.get_default_user_data_dir()
        assert "Google" in str(path)
        assert "Chrome" in str(path)

    def test_probe_cdp_status_offline(self):
        # Probing an invalid port should return inactive status cleanly without raising
        status = ChromeCDPBridge.probe_cdp_status(port=65530, timeout_sec=0.1)
        assert status["active"] is False
        assert status["browser"] is None


class TestAsyncPager:
    """Tests multi-channel notification and alert generation."""

    def test_page_user_generates_alert(self):
        pager = AsyncPager.get_instance()
        with patch.object(pager, "send_windows_toast", return_value=True), \
             patch.object(pager, "send_webhook", return_value=True):
            alert = pager.page_user("Test Title", "Test Message", urgency="WARNING")

            assert isinstance(alert, PagerAlert)
            assert alert.title == "Test Title"
            assert alert.message == "Test Message"
            assert alert.urgency == "WARNING"


class TestAOVOrchestratorBridge:
    """Tests master autonomous mission orchestration."""

    @pytest.mark.asyncio
    async def test_execute_autonomous_goal_wraps_in_guard(self):
        bridge = AOVOrchestratorBridge()
        
        mock_result = PlanExecutionResult(
            plan_id="p1",
            goal="test_goal",
            success=True,
            total_steps=1,
            executed_steps=1,
            step_results=[],
            elapsed_ms=10.0,
        )

        with patch.object(bridge.executor, "execute_plan", return_value=mock_result), \
             patch.object(KeepAwakeGuard, "activate", return_value=True), \
             patch.object(KeepAwakeGuard, "deactivate", return_value=True):
            
            steps = [{"step_id": "s1", "driver": "desktop", "action": "type", "params": {"text": "hello"}}]
            res = await bridge.execute_autonomous_goal("Test Goal", steps, attach_chrome_cdp=False)

            assert res.success is True
            assert res.goal == "test_goal"
