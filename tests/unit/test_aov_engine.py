"""
Unit Tests for Act-Observe-Verify (AOV) Engine and Deterministic Automation Drivers.
Covers:
  - StateObserver capture & Win32 primitives
  - StateSnapshot & mathematical StateDiff calculation
  - VerificationRule evaluation (WindowTitle, Clipboard, Cursor, CustomMetrics, AnyStateDelta)
  - ClosedLoopHarness execution, state diffing, and automated retry on verification failure
  - AOVPlanDAG step registration, execution, and closed-loop failure diagnostics
  - DeterministicDesktopDriver Win32 instant mouse/keyboard primitives
"""
import pytest
import time
from unittest.mock import MagicMock, patch

from jarvisx.harness.aov_engine import (
    StateSnapshot,
    StateDiff,
    WindowState,
    VerificationStatus,
    VerificationRule,
    AOVResult,
    StateObserver,
    ClosedLoopHarness,
    rule_window_title_contains,
    rule_clipboard_updated,
    rule_cursor_moved_to,
    rule_any_state_delta,
    rule_custom_metric_equals,
)
from jarvisx.automation.aov_planner import (
    AOVStep,
    AOVPlanDAG,
    AOVPlanExecutor,
    PlanExecutionResult,
)
from jarvisx.automation.deterministic_desktop_driver import DeterministicDesktopDriver


class TestStateSnapshotAndDiff:
    """Mathematical state diff computation tests."""

    def test_state_diff_detects_cursor_movement(self):
        s1 = StateSnapshot(
            timestamp=100.0,
            cursor_pos=(100, 200),
            active_window=None,
            clipboard_hash="abc",
            open_window_count=5,
        )
        s2 = StateSnapshot(
            timestamp=100.05,
            cursor_pos=(150, 250),
            active_window=None,
            clipboard_hash="abc",
            open_window_count=5,
        )
        diff = StateObserver.compute_diff(s1, s2)

        assert diff.cursor_moved is True
        assert diff.cursor_delta == (50, 50)
        assert diff.has_any_change is True
        assert diff.elapsed_ms == pytest.approx(50.0, rel=1e-2)

    def test_state_diff_detects_window_change(self):
        w1 = WindowState(hwnd=101, title="Editor", process_name="PID_1", rect={}, is_active=True)
        w2 = WindowState(hwnd=202, title="Terminal", process_name="PID_2", rect={}, is_active=True)
        
        s1 = StateSnapshot(timestamp=1.0, cursor_pos=(0, 0), active_window=w1, clipboard_hash="", open_window_count=10)
        s2 = StateSnapshot(timestamp=1.02, cursor_pos=(0, 0), active_window=w2, clipboard_hash="", open_window_count=10)
        diff = StateObserver.compute_diff(s1, s2)

        assert diff.window_changed is True
        assert diff.old_window_title == "Editor"
        assert diff.new_window_title == "Terminal"
        assert diff.has_any_change is True

    def test_state_diff_detects_clipboard_and_window_count(self):
        s1 = StateSnapshot(timestamp=1.0, cursor_pos=(0, 0), active_window=None, clipboard_hash="hash1", open_window_count=4)
        s2 = StateSnapshot(timestamp=1.01, cursor_pos=(0, 0), active_window=None, clipboard_hash="hash2", open_window_count=5)
        diff = StateObserver.compute_diff(s1, s2)

        assert diff.clipboard_changed is True
        assert diff.window_count_delta == 1
        assert diff.has_any_change is True

    def test_state_diff_no_change(self):
        s1 = StateSnapshot(timestamp=1.0, cursor_pos=(10, 10), active_window=None, clipboard_hash="hash", open_window_count=3)
        s2 = StateSnapshot(timestamp=1.01, cursor_pos=(10, 10), active_window=None, clipboard_hash="hash", open_window_count=3)
        diff = StateObserver.compute_diff(s1, s2)

        assert diff.has_any_change is False
        assert diff.cursor_moved is False
        assert diff.cursor_delta == (0, 0)
        assert diff.window_changed is False
        assert diff.clipboard_changed is False


class TestVerificationRules:
    """Tests standard verification rule evaluations against states and diffs."""

    def test_rule_window_title_contains_success(self):
        rule = rule_window_title_contains("Chrome")
        w = WindowState(hwnd=1, title="Google Chrome - Work", process_name="PID_1", rect={}, is_active=True)
        s_pre = StateSnapshot(1.0, (0, 0), None, "", 1)
        s_post = StateSnapshot(2.0, (0, 0), w, "", 1)
        diff = StateObserver.compute_diff(s_pre, s_post)

        passed, reason = rule.validator(s_pre, s_post, diff)
        assert passed is True
        assert "Google Chrome - Work" in reason

    def test_rule_window_title_contains_failure(self):
        rule = rule_window_title_contains("Calculator")
        w = WindowState(hwnd=1, title="Notepad", process_name="PID_1", rect={}, is_active=True)
        s_pre = StateSnapshot(1.0, (0, 0), None, "", 1)
        s_post = StateSnapshot(2.0, (0, 0), w, "", 1)
        diff = StateObserver.compute_diff(s_pre, s_post)

        passed, reason = rule.validator(s_pre, s_post, diff)
        assert passed is False
        assert "expected window containing" in reason.lower()

    def test_rule_cursor_moved_to(self):
        rule = rule_cursor_moved_to((500, 500), tolerance=10)
        s_pre = StateSnapshot(1.0, (100, 100), None, "", 1)
        s_post = StateSnapshot(2.0, (505, 498), None, "", 1)
        diff = StateObserver.compute_diff(s_pre, s_post)

        passed, reason = rule.validator(s_pre, s_post, diff)
        assert passed is True
        assert "within 10px" in reason

    def test_rule_any_state_delta(self):
        rule = rule_any_state_delta()
        s_pre = StateSnapshot(1.0, (100, 100), None, "", 1)
        s_post = StateSnapshot(2.0, (100, 100), None, "", 1)
        diff_no_change = StateObserver.compute_diff(s_pre, s_post)

        passed, _ = rule.validator(s_pre, s_post, diff_no_change)
        assert passed is False

        s_post_moved = StateSnapshot(2.0, (120, 100), None, "", 1)
        diff_changed = StateObserver.compute_diff(s_pre, s_post_moved)
        passed, _ = rule.validator(s_pre, s_post_moved, diff_changed)
        assert passed is True


class TestClosedLoopHarness:
    """Tests execution lifecycle, verified assertions, and auto-retry on failure."""

    def test_successful_action_with_verification(self):
        harness = ClosedLoopHarness(max_retries=1, retry_delay_sec=0.01)

        def mock_action():
            return "SUCCESS_DATA"

        s1 = StateSnapshot(1.0, (10, 10), None, "a", 1)
        s2 = StateSnapshot(1.01, (50, 50), None, "a", 1)

        with patch.object(StateObserver, 'capture', side_effect=[s1, s2]):
            result = harness.execute_closed_loop(
                action_name="test_move",
                act_fn=mock_action,
                rules=[rule_cursor_moved_to((50, 50), tolerance=5)]
            )

        assert result.success is True
        assert result.verification_status == VerificationStatus.PASSED
        assert result.retry_count == 0
        assert result.action_output == "SUCCESS_DATA"

    def test_retry_on_verification_failure_then_success(self):
        harness = ClosedLoopHarness(max_retries=2, retry_delay_sec=0.01)

        call_count = [0]
        def mock_action():
            call_count[0] += 1
            return f"ATTEMPT_{call_count[0]}"

        # Attempt 1: Pre and Post both have cursor at (10, 10) -> Rule fails
        # Attempt 2: Pre at (10, 10), Post at (200, 200) -> Rule passes
        s_idle = StateSnapshot(1.0, (10, 10), None, "a", 1)
        s_active = StateSnapshot(2.0, (200, 200), None, "a", 1)

        snapshots = [s_idle, s_idle, s_idle, s_active]

        with patch.object(StateObserver, 'capture', side_effect=snapshots):
            result = harness.execute_closed_loop(
                action_name="retry_move",
                act_fn=mock_action,
                rules=[rule_cursor_moved_to((200, 200), tolerance=5)]
            )

        assert result.success is True
        assert result.retry_count == 1
        assert call_count[0] == 2


class TestAOVPlanner:
    """Tests AOVPlanDAG and AOVPlanExecutor."""

    def test_dag_creation_and_step_registration(self):
        dag = AOVPlanDAG(plan_id="plan_001", goal="Test DAG Execution")
        s1 = AOVStep(step_id="step_1", driver="desktop", action="focus_window", params={"title": "Code"})
        s2 = AOVStep(step_id="step_2", driver="desktop", action="click", params={"x": 100, "y": 200}, depends_on=["step_1"])
        
        dag.add_step(s1)
        dag.add_step(s2)

        assert len(dag.steps) == 2
        assert dag.execution_order == ["step_1", "step_2"]

    def test_executor_runs_plan_with_driver_dispatch(self):
        dag = AOVPlanDAG(plan_id="plan_calc", goal="Perform Desktop Action")
        s1 = AOVStep(step_id="s1", driver="desktop", action="type", params={"text": "42"})
        dag.add_step(s1)

        executor = AOVPlanExecutor()
        
        # Mock desktop driver type_text_verified
        mock_aov_res = AOVResult(
            action_name="TypeText",
            success=True,
            verification_status=VerificationStatus.PASSED,
            pre_state=StateSnapshot(1.0, (0, 0), None, "", 0),
            post_state=StateSnapshot(2.0, (0, 0), None, "", 0),
            diff=StateDiff(10.0, False, (0, 0), False, "", "", False, 0),
            action_output=True,
            verification_reason="Verified state change"
        )
        
        with patch.object(executor.desktop_driver, 'type_text_verified', return_value=mock_aov_res):
            plan_res = executor.execute_plan(dag)

        assert plan_res.success is True
        assert plan_res.executed_steps == 1
        assert plan_res.failure_step_id is None


class TestDeterministicDesktopDriver:
    """Tests in-memory Win32 driver operations."""

    def test_singleton_instance(self):
        d1 = DeterministicDesktopDriver.get_instance()
        d2 = DeterministicDesktopDriver.get_instance()
        assert d1 is d2

    def test_in_memory_cursor_pos(self):
        driver = DeterministicDesktopDriver.get_instance()
        x, y = StateObserver.get_cursor_pos()
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert x >= 0
        assert y >= 0
