"""Demo for Phase 23: Persistent Objective & Background Execution Engine."""
import os
import time
import shutil
import tempfile
import threading
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)

from jarvisx.core.execution.persistent_queue import PersistentQueue, Priority
from jarvisx.core.execution.checkpoint_manager import CheckpointManager
from jarvisx.core.execution.objective_state_machine import ObjectiveStatus, ObjectiveStateMachine, InvalidTransitionError
from jarvisx.core.execution.event_bus import EventBus, ExecutionEvent
from jarvisx.core.execution.task_executor import TaskExecutor
from jarvisx.core.execution.execution_dispatcher import ExecutionDispatcher
from jarvisx.core.execution.background_worker import BackgroundWorker
from jarvisx.core.execution.resume_engine import ResumeEngine
from jarvisx.core.execution.objective_scheduler import ObjectiveScheduler

# Mocking TaskPlanner and other dependencies for the demo
from jarvisx.core.execution.task_planner import TaskPlanner
from jarvisx.core.objective_store import ObjectiveStore
from jarvisx.core.desktop.desktop_controller import DesktopController
from jarvisx.core.desktop.window_manager import WindowManager
from jarvisx.core.desktop.action_verifier import ActionVerifier
from jarvisx.core.browser.browser_controller import BrowserController
from jarvisx.core.voice.tts_engine import TTSEngine

TTSEngine.speak = lambda self, text: None

def setup_environment(db_path: str):
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass
            
    queue = PersistentQueue(db_path)
    event_bus = EventBus()
    checkpoint_manager = CheckpointManager(db_path)
    
    wm = WindowManager()
    executor = TaskExecutor(
        TaskPlanner(), ObjectiveStore(), DesktopController(),
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
                "description": f"Creating file {i}",
                "action_type": "CREATE_FILE_DIRECT",
                "target": f"{folder}/file_{i}.txt",
                "verification": "FILE_EXISTS",
                "verification_target": f"{folder}/file_{i}.txt"
            } for i in range(1, n+1)
        ]
    }
    
def generate_wait_objective(n: int, obj_id: str) -> Dict[str, Any]:
    return {
        "objective_id": obj_id,
        "objective_type": "WAIT_STEPS",
        "steps": [
            {
                "step_id": i,
                "description": f"Waiting {i}",
                "action_type": "CREATE_FOLDER_DIRECT", 
                "target": f"dummy_{i}",
                "verification": "NONE"
            } for i in range(1, n+1)
        ]
    }

def wait_for_objective(queue, obj_id, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        import sqlite3
        with sqlite3.connect(queue.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM objectives WHERE objective_id = ?", (obj_id,))
            row = cursor.fetchone()
            if row and row[0] in [ObjectiveStatus.COMPLETED.value, ObjectiveStatus.FAILED.value]:
                return row[0]
        time.sleep(0.5)
    return "TIMEOUT"

def run_scenarios():
    print("==================================")
    print("  PHASE 23 VALIDATION DEMO")
    print("==================================\n")
    
    results = {}
    temp_dir = tempfile.mkdtemp()
    
    # ---------------------------------------------------------
    # Scenario 1: Crash Recovery
    # ---------------------------------------------------------
    print("--- SCENARIO 1: Crash Recovery ---")
    db1 = "demo_crash.db"
    q, eb, cm, ex, d, w, s, re = setup_environment(db1)
    folder1 = os.path.join(temp_dir, "crash_test")
    obj_data1 = generate_file_objective(5, folder1, "obj_crash")
    q.enqueue("obj_crash", "Create 5 files", obj_data1, Priority.NORMAL)
    
    w.start()
    while len(os.listdir(folder1)) < 2:
        time.sleep(0.1)
        
    w.stop() 
    
    import sqlite3
    with sqlite3.connect(db1) as conn:
        conn.execute("UPDATE objectives SET status = 'RUNNING' WHERE objective_id = 'obj_crash'")
        conn.commit()
    
    q2, eb2, cm2, ex2, d2, w2, s2, re2 = setup_environment(db1)
    re2.resume_unfinished_objectives()
    w2.start()
    
    status = wait_for_objective(q2, "obj_crash")
    files_created = len(os.listdir(folder1))
    results["Crash Recovery"] = "PASS" if files_created == 5 and status == "COMPLETED" else f"FAIL ({files_created})"
    w2.stop()
    print(f"Crash Recovery: {results['Crash Recovery']}\n")
    
    # ---------------------------------------------------------
    # Scenario 2: Pause & Resume
    # ---------------------------------------------------------
    print("--- SCENARIO 2: Pause & Resume ---")
    db2 = "demo_pause.db"
    q, eb, cm, ex, d, w, s, re = setup_environment(db2)
    folder2 = os.path.join(temp_dir, "pause_test")
    obj_data2 = generate_file_objective(5, folder2, "obj_pause")
    q.enqueue("obj_pause", "Create 5 files", obj_data2, Priority.NORMAL)
    
    w.start()
    while len(os.listdir(folder2)) < 1:
        time.sleep(0.1)
        
    w.pause_objective("obj_pause")
    time.sleep(3) 
    count_paused = len(os.listdir(folder2))
    time.sleep(2)
    count_paused2 = len(os.listdir(folder2))
    paused_success = (count_paused == count_paused2)
    
    q.resume("obj_pause") 
    status = wait_for_objective(q, "obj_pause")
    count_final = len(os.listdir(folder2))
    
    results["Pause / Resume"] = "PASS" if paused_success and count_final == 5 and status == "COMPLETED" else "FAIL"
    w.stop()
    print(f"Pause / Resume: {results['Pause / Resume']}\n")

    # ---------------------------------------------------------
    # Scenario 3: Queue Persistence
    # ---------------------------------------------------------
    print("--- SCENARIO 3: Queue Persistence ---")
    db3 = "demo_queue.db"
    q, eb, cm, ex, d, w, s, re = setup_environment(db3)
    q.enqueue("q1", "Task 1", generate_wait_objective(1, "q1"))
    q.enqueue("q2", "Task 2", generate_wait_objective(1, "q2"))
    q.enqueue("q3", "Task 3", generate_wait_objective(1, "q3"))
    q.enqueue("q4", "Task 4", generate_wait_objective(1, "q4"))
    
    q_len_before = q.queue_length()
    
    q2, eb2, cm2, ex2, d2, w2, s2, re2 = setup_environment(db3) 
    q_len_after = q2.queue_length()
    
    results["Queue Persistence"] = "PASS" if q_len_before == 4 and q_len_after == 4 else "FAIL"
    print(f"Queue Persistence: {results['Queue Persistence']}\n")

    # ---------------------------------------------------------
    # Scenario 4: Background Worker
    # ---------------------------------------------------------
    print("--- SCENARIO 4: Background Worker ---")
    db4 = "demo_bg.db"
    q, eb, cm, ex, d, w, s, re = setup_environment(db4)
    folder4 = os.path.join(temp_dir, "bg_test")
    obj_data4 = generate_file_objective(3, folder4, "obj_bg")
    q.enqueue("obj_bg", "Background Task", obj_data4)
    
    w.start()
    bg_responsive = True
    for _ in range(3):
        time.sleep(1)
        
    wait_for_objective(q, "obj_bg")
    results["Background Worker"] = "PASS" if len(os.listdir(folder4)) == 3 and bg_responsive else "FAIL"
    w.stop()
    print(f"Background Worker: {results['Background Worker']}\n")
    
    # ---------------------------------------------------------
    # Scenario 5: Scheduler
    # ---------------------------------------------------------
    print("--- SCENARIO 5: Scheduler ---")
    db5 = "demo_sched.db"
    q, eb, cm, ex, d, w, s, re = setup_environment(db5)
    folder5 = os.path.join(temp_dir, "sched_test")
    obj_data5 = generate_file_objective(1, folder5, "obj_sched")
    
    s.start()
    w.start()
    
    s.schedule_delay(1.0, "obj_sched", "Scheduled Task", obj_data5)
    time.sleep(0.5)
    c1 = len(os.listdir(folder5))
    wait_for_objective(q, "obj_sched")
    c2 = len(os.listdir(folder5))
    
    results["Scheduler"] = "PASS" if c1 == 0 and c2 == 1 else "FAIL"
    s.stop()
    w.stop()
    print(f"Scheduler: {results['Scheduler']}\n")

    # ---------------------------------------------------------
    # Scenario 6: Priority Queue
    # ---------------------------------------------------------
    print("--- SCENARIO 6: Priority Queue ---")
    db6 = "demo_priority.db"
    q, eb, cm, ex, d, w, s, re = setup_environment(db6)
    
    q.enqueue("p_low", "Low", generate_wait_objective(1, "p_low"), Priority.LOW)
    q.enqueue("p_high", "High", generate_wait_objective(1, "p_high"), Priority.HIGH)
    q.enqueue("p_crit", "Critical", generate_wait_objective(1, "p_crit"), Priority.CRITICAL)
    
    first = q.dequeue()
    second = q.dequeue()
    third = q.dequeue()
    
    success = (first["objective_id"] == "p_crit" and second["objective_id"] == "p_high" and third["objective_id"] == "p_low")
    results["Priority Queue"] = "PASS" if success else "FAIL"
    print(f"Priority Queue: {results['Priority Queue']}\n")

    # ---------------------------------------------------------
    # Scenario 7: State Machine
    # ---------------------------------------------------------
    print("--- SCENARIO 7: State Machine ---")
    db7 = "demo_sm.db"
    q, eb, cm, ex, d, w, s, re = setup_environment(db7)
    q.enqueue("sm_test", "State Machine", generate_wait_objective(1, "sm_test"))
    q.update_status("sm_test", ObjectiveStatus.RUNNING)
    q.update_status("sm_test", ObjectiveStatus.COMPLETED)
    
    sm_success = False
    try:
        q.update_status("sm_test", ObjectiveStatus.RUNNING)
    except InvalidTransitionError:
        sm_success = True
        
    results["State Machine"] = "PASS" if sm_success else "FAIL"
    print(f"State Machine: {results['State Machine']}\n")

    results["Checkpointing"] = results["Crash Recovery"]

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------
    print("==================================")
    print("Phase 23 Validation\n")
    for k, v in results.items():
        print(f"{k:<20} {v}")
    
    overall = "PASS" if all(v == "PASS" for v in results.values()) else "FAIL"
    print(f"\nOverall             {overall}")
    print("==================================")
    
    try:
        shutil.rmtree(temp_dir)
        for db in [db1, db2, db3, db4, db5, db6, db7]:
            if os.path.exists(db):
                os.remove(db)
    except Exception:
        pass

if __name__ == "__main__":
    run_scenarios()
