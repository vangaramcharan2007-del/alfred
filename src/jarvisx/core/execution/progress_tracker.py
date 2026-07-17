"""Progress Tracker — tracks and formats execution state."""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ProgressTracker:
    """Maintains the execution state of an objective plan."""
    
    def __init__(self, plan: Dict[str, Any]):
        self.objective_id = plan["objective_id"]
        self.objective_type = plan["objective_type"]
        self.steps = plan["steps"]
        self.current_step_index = 0
        
        # Track status: "PENDING", "COMPLETED", "FAILED"
        self.step_status = {step["step_id"]: "PENDING" for step in self.steps}
        
    def get_current_step(self) -> Dict[str, Any]:
        """Returns the current step or None if finished."""
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
        
    def mark_completed(self) -> None:
        """Mark the current step as completed and advance."""
        current = self.get_current_step()
        if current:
            self.step_status[current["step_id"]] = "COMPLETED"
            self.current_step_index += 1
            
    def mark_failed(self) -> None:
        """Mark the current step as failed."""
        current = self.get_current_step()
        if current:
            self.step_status[current["step_id"]] = "FAILED"
            
    def is_finished(self) -> bool:
        """Check if all steps are processed."""
        return self.current_step_index >= len(self.steps)
        
    def get_summary(self) -> str:
        """Produce formatted string summary of progress."""
        lines = [f"Objective Progress: {self.objective_type}\n"]
        for step in self.steps:
            status = self.step_status[step["step_id"]]
            if status == "COMPLETED":
                mark = "[✓]"
            elif status == "FAILED":
                mark = "[X]"
            else:
                mark = "[ ]"
            lines.append(f"{mark} {step['description']}")
        return "\n".join(lines)

    def get_progress_string(self) -> str:
        """Returns 'Step X of Y' for voice."""
        current = self.current_step_index + 1
        total = len(self.steps)
        if current > total:
            current = total
        return f"Step {current} of {total}."
