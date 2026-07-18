"""Execution Coordinator — orchestrates Execute -> Verify -> Reflect -> Recover for a single step."""
import logging
from typing import Dict, Any, Callable, Tuple

from jarvisx.core.execution.event_bus import EventBus, ExecutionEvent
from jarvisx.core.execution.reflection_engine import ReflectionEngine
from jarvisx.core.execution.recovery_planner import RecoveryPlanner

logger = logging.getLogger(__name__)

class ExecutionCoordinator:
    """Coordinates the lifecycle of a single execution step."""
    
    def __init__(
        self, 
        event_bus: EventBus, 
        reflection_engine: ReflectionEngine,
        recovery_planner: RecoveryPlanner,
        executor_fn: Callable[[Dict[str, Any]], Tuple[bool, Exception]],
        verifier_fn: Callable[[Dict[str, Any]], bool]
    ):
        self.bus = event_bus
        self.reflection = reflection_engine
        self.recovery = recovery_planner
        self.executor_fn = executor_fn
        self.verifier_fn = verifier_fn

    def coordinate_step(self, step: Dict[str, Any]) -> bool:
        """Execute a step, verifying, reflecting, and recovering as needed."""
        self.bus.publish(ExecutionEvent.STEP_STARTED, {"step": step})
        
        max_retries = 3
        current_retry = 0
        
        while current_retry <= max_retries:
            # 1. Execute
            exec_success, error = self.executor_fn(step)
            
            # 2. Verify
            verif_success = False
            if exec_success:
                self.bus.publish(ExecutionEvent.VERIFICATION_STARTED, {"step": step})
                verif_success = self.verifier_fn(step)
                if verif_success:
                    self.bus.publish(ExecutionEvent.VERIFICATION_PASSED, {"step": step})
                else:
                    self.bus.publish(ExecutionEvent.VERIFICATION_FAILED, {"step": step})
                    
            # 3. Reflect
            reflection = self.reflection.reflect(step, exec_success, verif_success, error)
            self.bus.publish(ExecutionEvent.REFLECTION_COMPLETED, {"step": step, "reflection": reflection})
            
            if reflection.success:
                self.bus.publish(ExecutionEvent.STEP_COMPLETED, {"step": step})
                return True
                
            if not reflection.recoverable:
                self.bus.publish(ExecutionEvent.STEP_FAILED, {"step": step, "reason": "unrecoverable"})
                return False
                
            # 4. Recover
            self.bus.publish(ExecutionEvent.RECOVERY_STARTED, {"step": step, "strategy": reflection.recommendation})
            
            context = {
                "executor_fn": lambda s: self.executor_fn(s)[0] and self.verifier_fn(s),
                "max_retries": max_retries,
                "current_retry": current_retry
            }
            
            recovery_success = self.recovery.plan_and_recover(reflection, step, context)
            
            if recovery_success:
                self.bus.publish(ExecutionEvent.RECOVERY_SUCCEEDED, {"step": step})
                self.bus.publish(ExecutionEvent.STEP_COMPLETED, {"step": step})
                return True
                
            self.bus.publish(ExecutionEvent.RECOVERY_FAILED, {"step": step})
            current_retry += 1
            
        self.bus.publish(ExecutionEvent.STEP_FAILED, {"step": step, "reason": "max_retries_exceeded"})
        return False
