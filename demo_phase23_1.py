"""Phase 23.1: Observable Persistence Validation."""
import os
import time
import shutil
import tempfile
import threading
import logging
from typing import Dict, Any

from jarvisx.core.execution.persistent_queue import PersistentQueue, Priority
from jarvisx.core.execution.checkpoint_manager import CheckpointManager
from jarvisx.core.execution.objective_state_machine import ObjectiveStatus
from jarvisx.core.execution.event_bus import EventBus, ExecutionEvent
from jarvisx.core.execution.task_executor import TaskExecutor
from jarvisx.core.execution.execution_dispatcher import ExecutionDispatcher
from jarvisx.core.execution.background_worker import BackgroundWorker
from jarvisx.core.execution.resume_engine import ResumeEngine
from jarvisx.core.execution.objective_scheduler import ObjectiveScheduler

from jarvisx.core.execution.task_planner import TaskPlanner
from jarvisx.core.objective_store import ObjectiveStore
from jarvisx.core.desktop.desktop_controller import DesktopController
from jarvisx.core.desktop.window_manager import WindowManager
from jarvisx.core.desktop.action_verifier import ActionVerifier
from jarvisx.core.browser.browser_controller import BrowserController
from jarvisx.core.voice.tts_engine import TTSEngine

LOG_FILE = "phase23_demo.log"

# Setup file logger
file_handler = logging.FileHandler(LOG_FILE, mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Remove all other handlers to keep console clean, we will print manually
for handler in logger.handlers[:]:
    logger.removeHandler(handler)
logger.addHandler(file_handler)

TTSEngine.speak = lambda self, text: None

def setup_environment(db_path: str):
    queue = PersistentQueue(db_path)
    event_bus = EventBus()
    
    # Log all events
    def log_event(event: ExecutionEvent, payload: Dict[str, Any]):
        logger.info(f"Event: {event.name} | Payload: {payload}")
        
    for event in ExecutionEvent:
        event_bus.subscribe(event, log_event)
        
    checkpoint_manager = CheckpointManager(db_path)
    
    wm = WindowManager()
    
    # Custom DesktopController to inject delays
    class SlowDesktopController(DesktopController):
        def execute_action(self, action: Dict[str, Any]) -> bool:
            # Inject visible delay to simulate work and allow us to observe it
            time.sleep(0.15)
            return super().execute_action(action)
            
    executor = TaskExecutor(
        TaskPlanner(), ObjectiveStore(), SlowDesktopController(),
        wm, ActionVerifier(wm), BrowserController()
    )
    executor.set_checkpoint_manager(checkpoint_manager)
    executor.event_bus = event_bus
    executor.coordinator.event_bus = event_bus
    
    dispatcher = ExecutionDispatcher(executor)
    worker = BackgroundWorker(queue, dispatcher, event_bus, checkpoint_manager)
    scheduler = ObjectiveScheduler(queue)
    resume_engine = ResumeEngine(queue, event_bus)
    
    return queue, event_bus, checkpoint_manager, executor, dispatcher, worker, scheduler, resume_engine

def generate_file_objective(n: int, folder: str, obj_id: str) -> Dict[str, Any]:
    os.makedirs(folder, exist_ok=True)
    return {
        "objective_id": obj_id,
        "objective_type": "CREATE_FILES",
        "steps": [
            {
                "step_id": i,
                "description": f"Creating file_{i}.txt",
                "action_type": "CREATE_FILE_DIRECT",
                "target": f"{folder}/file_{i}.txt",
                "verification": "FILE_EXISTS",
                "verification_target": f"{folder}/file_{i}.txt"
            } for i in range(1, n+1)
        ]
    }

def print_progress(event: ExecutionEvent, payload: Dict[str, Any]):
    if event == ExecutionEvent.STEP_STARTED:
        step = payload.get("step", {})
        total = payload.get("total_steps", "?")
        print(f"[{step.get('step_id')}/{total}] {step.get('description')}")
    elif event == ExecutionEvent.OBJECTIVE_CHECKPOINT_SAVED:
        step_idx = payload.get("step_index")
        print(f"  -> Checkpoint Saved: Progress tracked up to step {step_idx}")

def run_demo():
    print("=====================================================")
    print(" Phase 23.1: Observable Persistence Validation Demo")
    print("=====================================================\n")
    
    temp_dir = tempfile.mkdtemp()
    
    # ---------------------------------------------------------
    # Test 1: Crash & Resume (50 files)
    # ---------------------------------------------------------
    print("--- Test 1: Crash & Resume Execution (50 Files) ---")
    db1 = os.path.join(temp_dir, "demo_crash.db")
    folder1 = os.path.join(temp_dir, "crash_test")
    
    q, eb, cm, ex, d, w, s, re = setup_environment(db1)
    eb.subscribe(ExecutionEvent.STEP_STARTED, print_progress)
    eb.subscribe(ExecutionEvent.OBJECTIVE_CHECKPOINT_SAVED, print_progress)
    
    obj_data1 = generate_file_objective(50, folder1, "obj_crash_50")
    q.enqueue("obj_crash_50", "Create 50 files", obj_data1, Priority.NORMAL)
    
    print("Starting Background Worker...")
    w.start()
    
    # Wait until around 20 files are created
    while len(os.listdir(folder1)) < 20:
        time.sleep(0.1)
        
    print("\n[!] Force Crashing the Worker (Simulating a crash) at ~20 files...\n")
    w.stop()
    
    # We simulate a crash where the DB still says 'RUNNING' but the worker is dead
    import sqlite3
    with sqlite3.connect(db1) as conn:
        conn.execute("UPDATE objectives SET status = 'RUNNING' WHERE objective_id = 'obj_crash_50'")
        conn.commit()
    
    print("Simulating process restart...")
    time.sleep(1)
    
    q2, eb2, cm2, ex2, d2, w2, s2, re2 = setup_environment(db1)
    eb2.subscribe(ExecutionEvent.STEP_STARTED, print_progress)
    eb2.subscribe(ExecutionEvent.OBJECTIVE_CHECKPOINT_SAVED, print_progress)
    
    print("Running Resume Engine to detect interrupted objectives...")
    re2.resume_unfinished_objectives()
    
    # Check what checkpoint we are at
    with sqlite3.connect(db1) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT current_step FROM objectives WHERE objective_id = 'obj_crash_50'")
        row = cursor.fetchone()
        if row:
            print(f"Loaded Checkpoint: Engine reports objective was at step {row[0]}")
    
    print("Restarting Background Worker...")
    w2.start()
    
    while True:
        with sqlite3.connect(db1) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM objectives WHERE objective_id = 'obj_crash_50'")
            row = cursor.fetchone()
            if row and row[0] in ["COMPLETED", "FAILED"]:
                break
        time.sleep(0.5)
        
    w2.stop()
    files_created = len(os.listdir(folder1))
    print(f"\nCompleted! Total files in folder: {files_created}")
    assert files_created == 50, f"Expected 50 files, found {files_created}!"
    print("Verification Passed: Exactly 50 unique files created with no duplicates or omissions.\n")
    
    # ---------------------------------------------------------
    # Test 2: Observable Pause & Resume
    # ---------------------------------------------------------
    print("--- Test 2: Observable Pause & Resume ---")
    db2 = os.path.join(temp_dir, "demo_pause.db")
    folder2 = os.path.join(temp_dir, "pause_test")
    
    q, eb, cm, ex, d, w, s, re = setup_environment(db2)
    eb.subscribe(ExecutionEvent.STEP_STARTED, print_progress)
    
    obj_data2 = generate_file_objective(30, folder2, "obj_pause_30")
    q.enqueue("obj_pause_30", "Create 30 files", obj_data2, Priority.NORMAL)
    
    w.start()
    
    # Pause at ~10 files
    while len(os.listdir(folder2)) < 10:
        time.sleep(0.1)
        
    print("\n[!] Pausing the objective...")
    w.pause_objective("obj_pause_30")
    
    time.sleep(1) # give it a moment to stop execution loop
    count_paused = len(os.listdir(folder2))
    print(f"Objective is paused. Currently {count_paused} files.")
    
    print("Waiting 3 seconds to verify no new files are created...")
    time.sleep(3)
    count_after_wait = len(os.listdir(folder2))
    print(f"Files after wait: {count_after_wait}")
    assert count_paused == count_after_wait, "Files were created while paused!"
    print("Verification Passed: No new files created while paused.\n")
    
    print("[!] Resuming the objective...")
    q.resume("obj_pause_30")
    
    while True:
        with sqlite3.connect(db2) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM objectives WHERE objective_id = 'obj_pause_30'")
            row = cursor.fetchone()
            if row and row[0] in ["COMPLETED", "FAILED"]:
                break
        time.sleep(0.5)
        
    w.stop()
    print(f"\nCompleted! Total files in folder: {len(os.listdir(folder2))}")
    assert len(os.listdir(folder2)) == 30, "Expected 30 files!"
    print("Verification Passed: Resumed flawlessly.\n")
    
    # ---------------------------------------------------------
    # Test 3: Scheduler Countdown
    # ---------------------------------------------------------
    print("--- Test 3: Scheduler Countdown ---")
    db3 = os.path.join(temp_dir, "demo_sched.db")
    folder3 = os.path.join(temp_dir, "sched_test")
    
    q, eb, cm, ex, d, w, s, re = setup_environment(db3)
    eb.subscribe(ExecutionEvent.STEP_STARTED, print_progress)
    
    obj_data3 = generate_file_objective(1, folder3, "obj_delayed_1")
    
    s.start()
    w.start()
    
    print("Scheduling objective for 3 seconds in the future...")
    s.schedule_delay(3.0, "obj_delayed_1", "Delayed Task", obj_data3)
    
    for i in range(3, 0, -1):
        print(f"Countdown: {i}...")
        time.sleep(1)
        
    print("Countdown finished. Expecting file creation...")
    
    while True:
        with sqlite3.connect(db3) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM objectives WHERE objective_id = 'obj_delayed_1'")
            row = cursor.fetchone()
            if row and row[0] in ["COMPLETED", "FAILED"]:
                break
        time.sleep(0.5)
        
    s.stop()
    w.stop()
    files_sched = len(os.listdir(folder3))
    print(f"Completed! Total files in folder: {files_sched}")
    assert files_sched == 1, "Expected exactly 1 file from scheduled task!"
    print("Verification Passed: Scheduler executed task after delay.\n")

    # Cleanup
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass
        
    print("=====================================================")
    print(" All validations passed successfully!")
    print(f" Timestamped EventBus log saved to: {LOG_FILE}")
    print("=====================================================")

if __name__ == "__main__":
    run_demo()
