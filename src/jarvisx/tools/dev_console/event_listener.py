"""Event Listener for the Jarvis X Developer Console."""
import time
import logging
from typing import Dict, Any

from jarvisx.core.execution.event_bus import EventBus, ExecutionEvent
from jarvisx.tools.dev_console.state import ConsoleState

logger = logging.getLogger(__name__)

class ConsoleEventListener:
    """Subscribes to EventBus and updates ConsoleState."""
    
    def __init__(self, event_bus: EventBus, state: ConsoleState):
        self.event_bus = event_bus
        self.state = state
        self._subscribe_all()
        
    def _subscribe_all(self):
        for event in ExecutionEvent:
            self.event_bus.subscribe(event, self._handle_event)
            
    def _handle_event(self, event: ExecutionEvent, payload: Dict[str, Any]):
        """Update state based on real-time execution events."""
        self.state.add_event(event.name)
        
        with self.state.lock:
            if event == ExecutionEvent.OBJECTIVE_STARTED:
                self.state.objective_id = payload.get("objective_id", "")
                self.state.objective_name = payload.get("objective_text", "")
                self.state.objective_status = "RUNNING"
                self.state.start_time = time.time()
                self.state.set_active_stage("Planner")
                
            elif event == ExecutionEvent.OBJECTIVE_PAUSED:
                self.state.objective_status = "PAUSED"
                
            elif event == ExecutionEvent.OBJECTIVE_RESUMED:
                self.state.objective_status = "RUNNING"
                self.state.set_active_stage("Executor")
                
            elif event == ExecutionEvent.OBJECTIVE_RESTARTED:
                self.state.objective_status = "RUNNING"
                
            elif event == ExecutionEvent.OBJECTIVE_COMPLETED:
                self.state.objective_status = "COMPLETED"
                self.state.set_active_stage("Completed")
                if self.state.start_time:
                    self.state.elapsed_time = time.time() - self.state.start_time
                    
            elif event == ExecutionEvent.OBJECTIVE_FAILED:
                self.state.objective_status = "FAILED"
                self.state.set_active_stage("Completed")
                
            elif event == ExecutionEvent.TASK_STARTED:
                self.state.set_active_stage("Planner")
                
            elif event == ExecutionEvent.STEP_STARTED:
                step_data = payload.get("step", {})
                self.state.current_step = step_data.get("step_id", 0)
                self.state.total_steps = payload.get("total_steps", self.state.total_steps)
                self.state.remaining_steps = self.state.total_steps - self.state.current_step
                self.state.current_action = step_data.get("action_type", "")
                self.state.current_target = step_data.get("target", "")
                self.state.set_active_stage("Executor")
                
            elif event == ExecutionEvent.STEP_COMPLETED:
                pass
                
            elif event == ExecutionEvent.VERIFICATION_STARTED:
                self.state.set_active_stage("Verifier")
                
            elif event == ExecutionEvent.VERIFICATION_FAILED:
                self.state.verification_failures += 1
                self.state.set_active_stage("Reflection")
                
            elif event == ExecutionEvent.STEP_FAILED:
                self.state.set_active_stage("Reflection")
                
            elif event == ExecutionEvent.RECOVERY_STARTED:
                strategy = payload.get("strategy")
                if strategy:
                    self.state.current_recovery_strategy = strategy.name if hasattr(strategy, 'name') else str(strategy)
                self.state.set_active_stage("Recovery")
                
            elif event == ExecutionEvent.RECOVERY_SUCCEEDED:
                self.state.recoveries += 1
                self.state.retries += 1
                self.state.set_active_stage("Executor")
                
            elif event == ExecutionEvent.RECOVERY_FAILED:
                self.state.set_active_stage("Completed")
                
            elif event == ExecutionEvent.OBJECTIVE_CHECKPOINT_SAVED:
                self.state.checkpoint_index = payload.get("step", 0)
                self.state.db_status = "CONNECTED"
                
            elif event == ExecutionEvent.REFLECTION_COMPLETED:
                self.state.reflection_decisions += 1
                
            elif event == ExecutionEvent.BACKGROUND_WORKER_STARTED:
                self.state.worker_status = "ACTIVE"
                
            elif event == ExecutionEvent.BACKGROUND_WORKER_STOPPED:
                self.state.worker_status = "STOPPED"
