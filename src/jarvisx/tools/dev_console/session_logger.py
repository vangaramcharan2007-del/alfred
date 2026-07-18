"""Handles session logging and failure snapshots."""
import os
import time
import json
import logging
from typing import Any, Dict

from jarvisx.tools.dev_console.state import ConsoleState

logger = logging.getLogger(__name__)

class SessionLogger:
    """Writes JSON execution session logs and failure snapshots."""
    
    def __init__(self, log_dir: str = "logs"):
        self.sessions_dir = os.path.join(log_dir, "sessions")
        self.failures_dir = os.path.join(log_dir, "failures")
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.failures_dir, exist_ok=True)
        
    def write_session(self, state: ConsoleState):
        """Save standard execution session log."""
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.sessions_dir, f"{timestamp}.json")
        data = self._state_to_dict(state)
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write session log: {e}")
            
    def write_failure_snapshot(self, state: ConsoleState):
        """Save a snapshot diagnostic dump on failure."""
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.failures_dir, f"{timestamp}.json")
        data = self._state_to_dict(state)
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write failure snapshot: {e}")
            
    def _state_to_dict(self, state: ConsoleState) -> Dict[str, Any]:
        with state.lock:
            return {
                "objective": {
                    "id": state.objective_id,
                    "name": state.objective_name,
                    "status": state.objective_status,
                    "final_step": state.current_step,
                    "total_steps": state.total_steps
                },
                "metrics": {
                    "elapsed_time": state.elapsed_time,
                    "average_step_time": state.average_step_time,
                    "fastest_step": state.fastest_step,
                    "slowest_step": state.slowest_step,
                },
                "recovery": {
                    "retries": state.retries,
                    "recoveries": state.recoveries,
                    "verification_failures": state.verification_failures,
                    "reflection_decisions": state.reflection_decisions,
                    "max_retry_chain": state.max_retry_chain
                },
                "timeline": list(state.events)
            }
