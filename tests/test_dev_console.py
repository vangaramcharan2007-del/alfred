"""Developer Console integration tests — Phase 23.3.

All tests use the REAL production execution pipeline with no mocks.
"""
import pytest
import os
import time
import sqlite3
import threading
from contextlib import closing

from jarvisx.tools.dev_console.app import ConsoleApp
from jarvisx.core.voice.tts_engine import TTSEngine
from jarvisx.core.execution.fault_injector import FaultInjector


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_file_objective(obj_id: str, folder: str, n: int) -> dict:
    return {
        "objective_id": obj_id,
        "objective_type": "CREATE_FILES",
        "steps": [
            {
                "step_id": i,
                "description": f"Created file_{i}.txt",
                "action_type": "CREATE_FILE_DIRECT",
                "target": f"{folder}/file_{i}.txt",
                "verification": "FILE_EXISTS",
                "verification_target": f"{folder}/file_{i}.txt",
            }
            for i in range(1, n + 1)
        ],
    }


def _wait_for_status(db_path: str, obj_id: str, expected: str, timeout: float = 60.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with closing(sqlite3.connect(db_path)) as conn:
                row = conn.execute(
                    "SELECT status FROM objectives WHERE objective_id = ?", (obj_id,)
                ).fetchone()
            if row and row[0] == expected:
                return True
        except Exception:
            pass
        time.sleep(0.3)
    return False


# ---------------------------------------------------------------------------
# Scenario 1 + 3: Fault injection causes FAILED → resume to COMPLETED
# ---------------------------------------------------------------------------

def test_scenario_1_and_3():
    """Injects a permanent fault at step 4 (0-based, exhausts all 4 retries) → FAILED.
    Then resumes from checkpoint → COMPLETED.
    
    max_triggers=-1 ensures all coordinator retries (0..3) encounter the fault.
    After the step exhausts max_retries, RecoveryPlanner fails → objective FAILED.
    """
    # Isolate from any previous test's faults
    FaultInjector().clear()

    db_path = f"test_console_{int(time.time())}.db"
    TTSEngine.speak = lambda self, text: None

    # ── Phase A: Run with permanent injected fault ──
    app1 = ConsoleApp()
    app1.db_path = db_path
    app1.setup_engine()

    desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_Phase23_Demo_Test")
    if os.path.exists(desktop_folder):
        import shutil
        shutil.rmtree(desktop_folder)
    os.makedirs(desktop_folder, exist_ok=True)

    obj_id = f"demo_files_{int(time.time())}"
    obj_data = _make_file_objective(obj_id, desktop_folder, 10)

    # max_triggers=-1: fault fires on every retry → exhausts coordinator → objective FAILS
    app1.fault_injector.inject_step_fault(
        obj_id, "CREATE_FILE_DIRECT", 4, RuntimeError("Simulated crash"), max_triggers=-1
    )

    from jarvisx.core.execution.persistent_queue import Priority
    app1.queue.enqueue(obj_id, "Create 10 files", obj_data, Priority.NORMAL)

    app1.worker.start()

    # objective should FAIL because the fault is permanent (all retries fail)
    assert _wait_for_status(db_path, obj_id, "FAILED", timeout=60), "Objective did not reach FAILED in time"
    app1.worker.stop()

    # Verify DB state
    with closing(sqlite3.connect(db_path)) as conn:
        row = conn.execute(
            "SELECT status, current_step FROM objectives WHERE objective_id = ?", (obj_id,)
        ).fetchone()
    assert row is not None
    assert row[0] == "FAILED", f"Expected FAILED, got {row[0]}"
    # steps 0–3 completed successfully, step 4 failed → current_step should be 4
    assert row[1] == 4, f"Expected current_step=4, got {row[1]}"

    # Simulate hard crash: mark back to RUNNING so resume_engine picks it up
    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute("UPDATE objectives SET status = 'RUNNING' WHERE objective_id = ?", (obj_id,))
        conn.commit()

    # ── Phase B: Resume ──
    FaultInjector().clear()  # Clear permanent fault so resume completes

    app2 = ConsoleApp()
    app2.db_path = db_path
    app2.setup_engine()

    with closing(sqlite3.connect(app2.db_path)) as conn:
        row = conn.execute(
            "SELECT objective_id, status, current_step, total_steps "
            "FROM objectives WHERE status NOT IN ('COMPLETED','FAILED','CANCELLED') LIMIT 1"
        ).fetchone()
    assert row is not None, "No resumable objective found after simulated crash"
    assert row[0] == obj_id
    assert row[2] == 4, f"Expected queue step=4, got {row[2]}"

    app2.resume_engine.resume_unfinished_objectives()
    app2.worker.start()

    assert _wait_for_status(db_path, obj_id, "COMPLETED", timeout=90), "Objective did not COMPLETE after resume"
    app2.worker.stop()

    with closing(sqlite3.connect(db_path)) as conn:
        row = conn.execute(
            "SELECT status, current_step FROM objectives WHERE objective_id = ?", (obj_id,)
        ).fetchone()
    assert row[0] == "COMPLETED", f"Expected COMPLETED, got {row[0]}"
    assert row[1] == 10, f"Expected current_step=10, got {row[1]}"

    FaultInjector().clear()


# ---------------------------------------------------------------------------
# Scenario 2: Pause → Resume
# ---------------------------------------------------------------------------

def test_scenario_2():
    """Start worker paused. Objective stays QUEUED. Resume → COMPLETED."""
    FaultInjector().clear()

    db_path = f"test_console_pause_{int(time.time())}.db"
    TTSEngine.speak = lambda self, text: None

    # Use a guaranteed-writable tmp path for the file
    folder = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_Pause_Test")
    os.makedirs(folder, exist_ok=True)

    app = ConsoleApp()
    app.db_path = db_path
    app.setup_engine()

    obj_id = f"demo_pause_{int(time.time())}"
    target_file = os.path.join(folder, "pause_test.txt")
    obj_data = {
        "objective_id": obj_id,
        "objective_type": "CREATE_FILES",
        "steps": [
            {
                "step_id": 1,
                "description": "Create pause test file",
                "action_type": "CREATE_FILE_DIRECT",
                "target": target_file,
                "verification": "FILE_EXISTS",
                "verification_target": target_file,
            }
        ],
    }

    from jarvisx.core.execution.persistent_queue import Priority
    app.queue.enqueue(obj_id, "Pause Test", obj_data, Priority.NORMAL)

    # Start paused — nothing should dequeue
    app.worker.start(start_paused=True)

    time.sleep(2.0)

    # While paused: objective must still be QUEUED
    with closing(sqlite3.connect(app.db_path)) as conn:
        row = conn.execute(
            "SELECT status FROM objectives WHERE objective_id = ?", (obj_id,)
        ).fetchone()
    assert row is not None
    assert row[0] == "QUEUED", f"Expected QUEUED while paused, got {row[0]}"

    # Resume
    app.worker.resume()

    assert _wait_for_status(db_path, obj_id, "COMPLETED", timeout=30), "Objective did not COMPLETE after resume"
    app.worker.stop()

    with closing(sqlite3.connect(app.db_path)) as conn:
        row = conn.execute(
            "SELECT status FROM objectives WHERE objective_id = ?", (obj_id,)
        ).fetchone()
    assert row[0] == "COMPLETED", f"Expected COMPLETED, got {row[0]}"

    FaultInjector().clear()
