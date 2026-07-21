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
        
    def write_session(self, state: ConsoleState, validation_summary: Dict[str, Any] = None):
        """Save standard execution session log in both JSON and TXT format."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # We need git commit hash if available
        commit_hash = "unknown"
        try:
            import subprocess
            res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
            if res.returncode == 0:
                commit_hash = res.stdout.strip()
        except Exception:
            pass
            
        data = self._state_to_dict(state)
        data["system"] = {
            "version": "Phase 23.3",
            "git_commit": commit_hash
        }
        if validation_summary:
            data["validation"] = validation_summary
            
        json_filename = os.path.join(self.sessions_dir, f"session_{timestamp}.json")
        log_filename = os.path.join(self.sessions_dir, f"session_{timestamp}.log")
        
        try:
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            with open(log_filename, "w", encoding="utf-8") as f:
                f.write(f"JARVIS X SESSION LOG ({timestamp})\n")
                f.write(f"Version: Phase 23.3 | Commit: {commit_hash}\n")
                f.write("="*50 + "\n")
                f.write(f"Objective ID: {data['objective']['id']}\n")
                f.write(f"Status: {data['objective']['status']}\n")
                f.write(f"Execution Time: {data['metrics']['elapsed_time']:.2f}s\n")
                f.write(f"Total Events: {len(data['timeline'])}\n")
                f.write(f"Retries: {data['recovery']['retries']}\n")
                f.write(f"Recoveries: {data['recovery']['recoveries']}\n")
                f.write(f"Recovered Steps: {data['objective'].get('checkpoint_index', 0)}\n")
                
                if validation_summary:
                    f.write("\nValidation Summary:\n")
                    f.write(f"SQLite Integrity: {validation_summary.get('sqlite_integrity', 'UNKNOWN')}\n")
                    f.write(f"Overall Status: {validation_summary.get('overall_status', 'UNKNOWN')}\n")
                
                f.write("\nTimeline:\n")
                for t, e in data['timeline']:
                    f.write(f"[{t}] {e}\n")
                    
        except Exception as e:
            logger.error(f"Failed to write session log: {e}")
            
    def write_failure_snapshot(self, state: ConsoleState):
        """Save a snapshot diagnostic dump on failure."""
        self.write_session(state, {"overall_status": "CRASH", "sqlite_integrity": "N/A"})
            
    def _state_to_dict(self, state: ConsoleState) -> Dict[str, Any]:
        with state.lock:
            return {
                "objective": {
                    "id": state.objective_id,
                    "name": state.objective_name,
                    "status": state.objective_status,
                    "final_step": state.current_step,
                    "total_steps": state.total_steps,
                    "checkpoint_index": state.checkpoint_index
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
