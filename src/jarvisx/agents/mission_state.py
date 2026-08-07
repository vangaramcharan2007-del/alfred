"""Mission State Machine for Phase 91 Autonomous Mission Brain."""

from __future__ import annotations
import time
from enum import Enum
from typing import Dict, Any, List, Optional


class State(str, Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    WAITING = "WAITING"
    REPLANNING = "REPLANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MissionStateMachine:
    """Formal deterministic state machine for autonomous mission lifecycle."""

    # Valid State Transitions
    TRANSITIONS: Dict[State, List[State]] = {
        State.CREATED: [State.PLANNING, State.FAILED],
        State.PLANNING: [State.EXECUTING, State.WAITING, State.FAILED],
        State.EXECUTING: [State.WAITING, State.REPLANNING, State.COMPLETED, State.FAILED],
        State.WAITING: [State.EXECUTING, State.REPLANNING, State.FAILED],
        State.REPLANNING: [State.EXECUTING, State.WAITING, State.FAILED],
        State.COMPLETED: [],
        State.FAILED: [State.REPLANNING],  # Can recover via replan
    }

    def __init__(self, mission_id: str, goal: str):
        self.mission_id = mission_id
        self.goal = goal
        self.current_state: State = State.CREATED
        self.history: List[Dict[str, Any]] = [
            {"state": State.CREATED.value, "timestamp": time.time(), "reason": "Mission initialized"}
        ]

    def can_transition_to(self, new_state: State) -> bool:
        """Check if transition from current state to new state is valid."""
        return new_state in self.TRANSITIONS.get(self.current_state, [])

    def transition_to(self, new_state: State, reason: str = "") -> State:
        """Execute state transition if valid, otherwise raise StateTransitionError."""
        if not self.can_transition_to(new_state):
            raise ValueError(
                f"Invalid mission state transition: Cannot move from {self.current_state.value} to {new_state.value}."
            )
        self.current_state = new_state
        self.history.append({
            "state": new_state.value,
            "timestamp": time.time(),
            "reason": reason
        })
        return self.current_state

    def is_finished(self) -> bool:
        """Check if mission has reached terminal state."""
        return self.current_state in (State.COMPLETED, State.FAILED)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "goal": self.goal,
            "current_state": self.current_state.value,
            "history": self.history,
        }
