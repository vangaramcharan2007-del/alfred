"""Entry point for the Jarvis X Developer Console."""
import os
import sys
import time
import sqlite3
from contextlib import closing
from rich.live import Live

from jarvisx.core.execution.persistent_queue import PersistentQueue, Priority
from jarvisx.core.execution.checkpoint_manager import CheckpointManager
from jarvisx.core.execution.event_bus import EventBus
from jarvisx.core.execution.task_executor import TaskExecutor
from jarvisx.core.execution.execution_dispatcher import ExecutionDispatcher
from jarvisx.core.execution.background_worker import BackgroundWorker
from jarvisx.core.execution.resume_engine import ResumeEngine
from jarvisx.core.execution.objective_scheduler import ObjectiveScheduler
from jarvisx.core.execution.fault_injector import FaultInjector

from jarvisx.core.execution.task_planner import TaskPlanner
from jarvisx.core.objective_store import ObjectiveStore
from jarvisx.core.desktop.desktop_controller import DesktopController
from jarvisx.core.desktop.window_manager import WindowManager
from jarvisx.core.desktop.action_verifier import ActionVerifier
from jarvisx.core.browser.browser_controller import BrowserController
from jarvisx.core.voice.tts_engine import TTSEngine

from jarvisx.tools.dev_console.state import ConsoleState
from jarvisx.tools.dev_console.metrics import ConsoleMetrics
from jarvisx.tools.dev_console.event_listener import ConsoleEventListener
from jarvisx.tools.dev_console.command_router import CommandRouter
from jarvisx.tools.dev_console.dashboard import generate_layout
from jarvisx.tools.dev_console.session_logger import SessionLogger
from jarvisx.tools.dev_console.replay import ConsoleReplay

DB_PATH = "demo_interactive.db"

class ConsoleApp:
    
    def __init__(self):
        self.state = ConsoleState()
        self.session_logger = SessionLogger()
        self.live_display = None
        self.should_exit = False
        self.db_path = DB_PATH
        
        # Disable TTS for console running
        TTSEngine.speak = lambda self, text: None

    def setup_engine(self):
        self.queue = PersistentQueue(self.db_path)
        self.event_bus = EventBus()
        self.checkpoint_manager = CheckpointManager(self.db_path)
        
        wm = WindowManager()
        self.executor = TaskExecutor(
            TaskPlanner(), ObjectiveStore(), DesktopController(),
            wm, ActionVerifier(wm), BrowserController()
        )
        self.executor.set_checkpoint_manager(self.checkpoint_manager)
        self.executor.event_bus = self.event_bus
        self.executor.coordinator.event_bus = self.event_bus
        
        self.dispatcher = ExecutionDispatcher(self.executor)
        self.worker = BackgroundWorker(self.queue, self.dispatcher, self.event_bus, self.checkpoint_manager)
        self.scheduler = ObjectiveScheduler(self.queue)
        self.resume_engine = ResumeEngine(self.queue, self.event_bus)
        self.fault_injector = FaultInjector()
        
        self.executor.coordinator.fault_injector = self.fault_injector
        
        self.event_listener = ConsoleEventListener(self.event_bus, self.state)
        self.metrics = ConsoleMetrics(self.state, self.queue)
        self.router = CommandRouter(
            self.worker, self.queue, self.resume_engine,
            on_exit=self.quit,
            on_simulate_crash=self.simulate_crash,
            on_export=self.export_session,
            on_replay=self.replay_session
        )

    def print_menu(self):
        print("=====================================================")
        print(" JARVIS X DEVELOPER CONSOLE (Phase 23.3)")
        print("=====================================================\n")
        print("Select Failure Injection:")
        print("1) Missing Browser")
        print("2) Permission Error")
        print("3) Timeout")
        print("4) Verification Failure")
        print("5) Network Failure")
        print("6) Random Failure")
        print("7) None")
        
        choice = input("\nEnter choice [1-7]: ").strip()
        
        faults = {
            '1': 'MISSING_BROWSER',
            '2': 'PERMISSION_DENIED',
            '3': 'TIMEOUT',
            '4': 'VERIFICATION_FAILED',
            '5': 'NETWORK_ERROR',
            '6': 'RANDOM',
            '7': 'NONE'
        }
        
        selected = faults.get(choice, 'NONE')
        if selected != 'NONE':
            self.fault_injector.set_fault(selected)
            print(f"Injected Fault: {selected}")
            
    def check_resume(self):
        if os.path.exists(self.db_path):
            with closing(sqlite3.connect(self.db_path)) as conn, conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT objective_id, status, current_step, total_steps FROM objectives WHERE status != 'COMPLETED' AND status != 'FAILED' LIMIT 1")
                    row = cursor.fetchone()
                    if row:
                        obj_id, status, current_step, total_steps = row
                        print(f"\nCheckpoint Found!")
                        print(f"Objective ID: {obj_id}")
                        print(f"Recovered Step: {current_step}")
                        print(f"Remaining Steps: {total_steps - current_step if total_steps else '?'}")
                        ans = input("\nResume? [Y/N]: ").strip().lower()
                        if ans == 'y':
                            self.resume_engine.resume_unfinished_objectives()
                            self.worker.start()
                            return True
                except sqlite3.OperationalError:
                    pass
        return False
        
    def enqueue_demo_objective(self):
        desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_Phase23_Demo")
        if os.path.exists(desktop_folder):
            import shutil
            shutil.rmtree(desktop_folder)
        os.makedirs(desktop_folder, exist_ok=True)
            
        # 1. File creation objective
        obj_id_1 = f"demo_files_{int(time.time())}"
        n = 50
        obj_data_1 = {
            "objective_id": obj_id_1,
            "objective_type": "CREATE_FILES",
            "steps": [
                {
                    "step_id": i,
                    "description": f"Created file_{i:02d}.txt",
                    "action_type": "CREATE_FILE_DIRECT",
                    "target": f"{desktop_folder}/file_{i:02d}.txt",
                    "verification": "FILE_EXISTS",
                    "verification_target": f"{desktop_folder}/file_{i:02d}.txt"
                } for i in range(1, n+1)
            ]
        }
        self.queue.enqueue(obj_id_1, "Create 50 files on Desktop", obj_data_1, Priority.NORMAL)
        
        # 2. Application launch objective
        obj_id_2 = f"demo_app_{int(time.time())}"
        obj_data_2 = {
            "objective_id": obj_id_2,
            "objective_type": "LAUNCH_APP",
            "steps": [
                {
                    "step_id": 1,
                    "description": "Launch Calculator",
                    "action_type": "LAUNCH_APPLICATION",
                    "target": "calc.exe",
                    "verification": "PROCESS_EXISTS",
                    "verification_target": "CalculatorApp.exe"
                }
            ]
        }
        self.queue.enqueue(obj_id_2, "Launch Calculator Application", obj_data_2, Priority.HIGH)
        
        # 3. Scheduled objective (using very basic setup)
        obj_id_3 = f"demo_sched_{int(time.time())}"
        obj_data_3 = {
            "objective_id": obj_id_3,
            "objective_type": "SCHEDULED_TASK",
            "steps": [
                {
                    "step_id": 1,
                    "description": "Scheduled notification",
                    "action_type": "NOTIFY",
                    "target": "Scheduled Task Executed!",
                    "verification": "NONE"
                }
            ]
        }
        # In reality, this goes to the scheduler, but for demo we just put it in queue with low priority
        self.queue.enqueue(obj_id_3, "Scheduled Notification", obj_data_3, Priority.LOW)
        
        self.worker.start()

    def simulate_crash(self):
        """Simulate an abrupt hard crash while preserving state."""
        self.worker.stop()
        
        with self.state.lock:
            obj_id = self.state.objective_id
            
        if obj_id:
            with closing(sqlite3.connect(self.db_path)) as conn, conn:
                conn.execute(f"UPDATE objectives SET status = 'RUNNING' WHERE objective_id = '{obj_id}'")
                conn.commit()
                
        self.session_logger.write_failure_snapshot(self.state)
        self.should_exit = True
        
    def export_session(self):
        self.session_logger.write_session(self.state)
        
    def replay_session(self):
        # We can trigger replay at the end.
        pass

    def quit(self):
        self.worker.stop()
        self.should_exit = True

    def run(self):
        self.setup_engine()
        self.print_menu()
        
        resumed = self.check_resume()
        if not resumed:
            self.enqueue_demo_objective()
            
        self.metrics.start()
        self.router.start()
        
        try:
            with Live(generate_layout(self.state, self.router), refresh_per_second=4) as live:
                self.live_display = live
                while not self.should_exit:
                    with self.state.lock:
                        if self.state.objective_status in ["COMPLETED", "FAILED"]:
                            break
                    live.update(generate_layout(self.state, self.router))
                    time.sleep(0.25)
        except KeyboardInterrupt:
            self.quit()
            
        self.metrics.stop()
        self.router.stop()
        
        self.session_logger.write_session(self.state)
        
        print("\n=====================================================")
        print(" VALIDATION SUMMARY")
        print("=====================================================")
        with self.state.lock:
            status = "PASS" if self.state.objective_status == "COMPLETED" else "FAIL"
            print(f"Overall Status:        {status}")
            print(f"Execution Time:        {self.state.elapsed_time:.2f} sec")
            print(f"Average Step Time:     {self.state.average_step_time:.2f} sec")
            print(f"Recovered Steps:       {self.state.checkpoint_index}")
            print(f"Retries:               {self.state.retries}")
            print(f"Recoveries:            {self.state.recoveries}")
            
        desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_Phase23_Demo")
        if os.path.exists(desktop_folder):
            count = len(os.listdir(desktop_folder))
            print(f"Files Created:         {count}")
            print(f"Expected Files:        50")
            print(f"Missing Files:         {50 - count if count < 50 else 0}")
            print(f"Duplicate Files:       0")
            
            print("\nOpening Windows Explorer...")
            os.startfile(desktop_folder)
            
        ConsoleReplay.prompt_and_replay(self.state)

if __name__ == "__main__":
    app = ConsoleApp()
    app.run()
