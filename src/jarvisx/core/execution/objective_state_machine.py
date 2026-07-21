"""Objective State Machine — enforces valid transitions for objective status."""
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class ObjectiveStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class ObjectiveStateMachine:
    """Manages legal state transitions for an objective."""
    
    # Define valid transitions (source -> list of allowed targets)
    VALID_TRANSITIONS = {
        ObjectiveStatus.QUEUED: [ObjectiveStatus.RUNNING],
        ObjectiveStatus.RUNNING: [
            ObjectiveStatus.PAUSED,
            ObjectiveStatus.COMPLETED,
            ObjectiveStatus.FAILED
        ],
        ObjectiveStatus.PAUSED: [
            ObjectiveStatus.QUEUED,
            ObjectiveStatus.RUNNING
        ],
        ObjectiveStatus.FAILED: [
            ObjectiveStatus.RUNNING,
            ObjectiveStatus.CANCELLED
        ],
        ObjectiveStatus.COMPLETED: [],
        ObjectiveStatus.CANCELLED: []
    }
    
    @staticmethod
    def transition(current_state: ObjectiveStatus, next_state: ObjectiveStatus) -> ObjectiveStatus:
        """
        Attempt to transition to next_state.
        Raises InvalidTransitionError if the transition is not allowed.
        """
        # Accept transition if it's the same state (no-op)
        if current_state == next_state:
            return next_state
            
        allowed = ObjectiveStateMachine.VALID_TRANSITIONS.get(current_state, [])
        if next_state not in allowed:
            error_msg = f"Invalid transition: {current_state.value} -> {next_state.value}"
            logger.error(error_msg)
            raise InvalidTransitionError(error_msg)
            
        return next_state
