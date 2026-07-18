"""Event Bus — publish/subscribe system for execution events."""
import logging
from enum import Enum, auto
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class ExecutionEvent(Enum):
    """Events emitted during the objective execution lifecycle."""
    OBJECTIVE_STARTED = auto()
    OBJECTIVE_COMPLETED = auto()
    OBJECTIVE_FAILED = auto()
    TASK_STARTED = auto()
    TASK_FINISHED = auto()
    STEP_STARTED = auto()
    STEP_COMPLETED = auto()
    STEP_FAILED = auto()
    VERIFICATION_STARTED = auto()
    VERIFICATION_PASSED = auto()
    VERIFICATION_FAILED = auto()
    REFLECTION_COMPLETED = auto()
    RECOVERY_STARTED = auto()
    RECOVERY_SUCCEEDED = auto()
    RECOVERY_FAILED = auto()


class EventBus:
    """Lightweight publish/subscribe event system."""
    
    def __init__(self):
        self._subscribers: Dict[ExecutionEvent, List[Callable]] = {}

    def subscribe(self, event: ExecutionEvent, callback: Callable) -> None:
        """Subscribe a callback to an event."""
        if event not in self._subscribers:
            self._subscribers[event] = []
        if callback not in self._subscribers[event]:
            self._subscribers[event].append(callback)

    def unsubscribe(self, event: ExecutionEvent, callback: Callable) -> None:
        """Unsubscribe a callback from an event."""
        if event in self._subscribers and callback in self._subscribers[event]:
            self._subscribers[event].remove(callback)

    def publish(self, event: ExecutionEvent, payload: Dict[str, Any]) -> None:
        """Publish an event with a payload to all subscribers."""
        if event in self._subscribers:
            for callback in self._subscribers[event]:
                try:
                    callback(event, payload)
                except Exception as e:
                    logger.error(f"Error in event subscriber for {event}: {e}")

# Global instance for easy access if dependency injection is not feasible everywhere
# However, the user request mentions "Prefer dependency injection".
