"""Console state for the Jarvis X Developer Console."""
import threading
from typing import Dict, Any, List
from collections import deque
import time

class ConsoleState:
    """Thread-safe store for all console dashboard metrics and states."""
    
    def __init__(self):
        self.lock = threading.RLock()
        
        # General Status
        self.objective_name = ""
        self.objective_id = ""
        self.objective_status = "IDLE"
        self.worker_status = "STOPPED"
        self.queue_size = 0
        self.scheduler_queue = 0
        
        # Progress
        self.current_step = 0
        self.total_steps = 0
        self.remaining_steps = 0
        self.current_action = ""
        self.current_target = ""
        self.checkpoint_index = 0
        
        # Timing
        self.start_time = None
        self.elapsed_time = 0.0
        self.average_step_time = 0.0
        self.fastest_step = 0.0
        self.slowest_step = 0.0
        
        self._step_durations = []
        
        # Debug States
        self.db_status = "DISCONNECTED"
        self.planner_state = "IDLE"
        self.executor_state = "IDLE"
        self.reflection_state = "IDLE"
        self.recovery_state = "IDLE"
        self.verifier_state = "IDLE"
        
        self.active_stage = "Planner" # Planner, Executor, Reflection, Recovery, Verifier, Completed
        self.current_recovery_strategy = "None"
        
        # Timeline
        self.events = deque(maxlen=100)
        
        # Recovery Stats
        self.retries = 0
        self.recoveries = 0
        self.permission_recoveries = 0
        self.alt_tool_recoveries = 0
        self.verification_failures = 0
        self.average_retry_time = 0.0
        self.max_retry_chain = 0
        self.reflection_decisions = 0
        
        # Latency / Wait Time
        self.queue_wait_time = 0.0
        self.worker_idle_time = 0.0
        self.checkpoint_save_latency = 0.0
        self.sqlite_latency = 0.0
        
        # System Resource
        self.cpu_percent = 0.0
        self.ram_percent = 0.0
        self.thread_count = 0
        self.worker_threads = 0
        self.sqlite_connections = 0
        self.background_tasks = 0
        
        # Multiple Objectives (Running, Queued, Paused, Completed)
        self.objectives_list = []
        
    def add_event(self, event_name: str):
        """Add an event to the timeline."""
        timestamp = time.strftime("%H:%M:%S")
        with self.lock:
            self.events.append((timestamp, event_name))
            
    def set_active_stage(self, stage: str):
        with self.lock:
            self.active_stage = stage
            if stage == "Planner":
                self.planner_state = "ACTIVE"
            elif stage == "Executor":
                self.executor_state = "ACTIVE"
            elif stage == "Reflection":
                self.reflection_state = "ACTIVE"
            elif stage == "Recovery":
                self.recovery_state = "ACTIVE"
            elif stage == "Verifier":
                self.verifier_state = "ACTIVE"
