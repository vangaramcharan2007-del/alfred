"""Phase 23.2: Interactive Observable Validation."""
import os
import time
import sqlite3
import threading
import logging
from typing import Dict, Any
from contextlib import closing

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

DB_PATH = "demo_interactive.db"
LOG_FILE = "phase23_interactive.log"

def setup_logging(is_resume: bool):
    mode = 'a' if is_resume else 'w'
    file_handler = logging.FileHandler(LOG_FILE, mode=mode)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(file_handler)

TTSEngine.speak = lambda self, text: None

def setup_environment(db_path: str):
    queue = PersistentQueue(db_path)
    event_bus = EventBus()
    
    def log_event(event: ExecutionEvent, payload: Dict[str, Any]):
        logger.info(f"Event: {event.name} | Payload: {payload}")
        if event == ExecutionEvent.STEP_STARTED:
            step = payload.get("step", {})
            total = payload.get("total_steps", "?")
            print(f"[{step.get('step_id'):02d}/{total}] {step.get('description')}")
            
    for event in ExecutionEvent:
        event_bus.subscribe(event, log_event)
        
    checkpoint_manager = CheckpointManager(db_path)
    
    wm = WindowManager()
    
    class SlowDesktopController(DesktopController):
        def execute_action(self, action: Dict[str, Any]) -> bool:
            time.sleep(0.500) # 500 ms delay
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
                "description": f"Created file_{i:02d}.txt",
                "action_type": "CREATE_FILE_DIRECT",
                "target": f"{folder}/file_{i:02d}.txt",
                "verification": "FILE_EXISTS",
                "verification_target": f"{folder}/file_{i:02d}.txt"
            } for i in range(1, n+1)
        ]
    }

def run_interactive_demo():
    print("=====================================================")
    print(" Phase 23.2: Interactive Observable Validation")
    print("=====================================================\n")
    
    desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_Phase23_Demo")
    q, eb, cm, ex, d, w, s, re = setup_environment(DB_PATH)
    
    # Check if objective exists
    is_resume = False
    current_step = 0
    if os.path.exists(DB_PATH):
        with closing(sqlite3.connect(DB_PATH)) as conn, conn:
            cursor = conn.cursor()
            # Handle case where table might not exist if DB just created
            try:
                cursor.execute("SELECT objective_id, status, current_step FROM objectives WHERE objective_id LIKE 'demo_50_%'")
                row = cursor.fetchone()
                if row:
                    obj_id, status, current_step = row
                    if status != 'COMPLETED':
                        is_resume = True
            except sqlite3.OperationalError:
                pass
                
    setup_logging(is_resume)

    if is_resume:
        print(f"Found checkpoint at step {current_step}")
        print("Resuming...")
        
        # In this demo, if it crashed, it might be stuck in RUNNING. Let's force it to RUNNING so resume catches it correctly if it wasn't.
        with closing(sqlite3.connect(DB_PATH)) as conn, conn:
            conn.execute(f"UPDATE objectives SET status = 'RUNNING' WHERE objective_id = '{obj_id}'")
            conn.commit()
            
        re.resume_unfinished_objectives()
        
        # Now it is QUEUED, start worker
        w.start()
        
        print("Waiting for completion...")
        while True:
            with closing(sqlite3.connect(DB_PATH)) as conn, conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT status FROM objectives WHERE objective_id = '{obj_id}'")
                row = cursor.fetchone()
                if row and row[0] in ["COMPLETED", "FAILED"]:
                    break
            time.sleep(0.5)
            
        w.stop()
        
        count = len(os.listdir(desktop_folder)) if os.path.exists(desktop_folder) else 0
        print(f"\nFinished! Folder contains {count} files.")
        
        print("\nOpening the folder in Windows Explorer so you can visually verify...")
        os.startfile(desktop_folder)
        
        # Cleanup DB for next time
        try:
            os.remove(DB_PATH)
        except OSError:
            pass
        
    else:
        # Initial run
            
        if os.path.exists(desktop_folder):
            import shutil
            shutil.rmtree(desktop_folder)
            
        obj_id = f"demo_50_{int(time.time())}"
        print(f"Target Folder: {desktop_folder}")
        obj_data = generate_file_objective(50, desktop_folder, obj_id)
        q.enqueue(obj_id, "Create 50 files on Desktop", obj_data, Priority.NORMAL)
        
        w.start()
        
        input("\nPress ENTER to simulate crash\n")
        
        w.stop()
        
        # Simulate abrupt failure
        with closing(sqlite3.connect(DB_PATH)) as conn, conn:
            conn.execute(f"UPDATE objectives SET status = 'RUNNING' WHERE objective_id = '{obj_id}'")
            conn.commit()
            
        print("\nWorker terminated. Please run this script again to resume.")

if __name__ == "__main__":
    run_interactive_demo()
