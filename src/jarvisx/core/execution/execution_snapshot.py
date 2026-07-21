"""Execution Snapshot — represents the immutable state of an objective."""
from dataclasses import dataclass, field
from typing import Dict, Any, List
import time

@dataclass
class ExecutionSnapshot:
    """A versioned, serializable snapshot of execution state."""
    objective_id: str
    current_step: int
    completed_steps: List[int] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    reflection_state: Dict[str, Any] = field(default_factory=dict)
    recovery_state: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a serializable dictionary."""
        return {
            "version": self.version,
            "objective_id": self.objective_id,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps,
            "variables": self.variables,
            "context": self.context,
            "reflection_state": self.reflection_state,
            "recovery_state": self.recovery_state,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionSnapshot":
        """Reconstruct from dictionary."""
        # Future-proofing: handle different versions if needed.
        return cls(
            version=data.get("version", 1),
            objective_id=data["objective_id"],
            current_step=data["current_step"],
            completed_steps=data.get("completed_steps", []),
            variables=data.get("variables", {}),
            context=data.get("context", {}),
            reflection_state=data.get("reflection_state", {}),
            recovery_state=data.get("recovery_state", {}),
            timestamp=data.get("timestamp", time.time())
        )
