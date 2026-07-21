"""Fault Injection Framework — simulates failures without modifying production systems."""
import logging
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)

class FaultInjector:
    """Injects controlled failures during testing or demos."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FaultInjector, cls).__new__(cls)
            cls._instance._faults = {}
        return cls._instance
        
    def inject_execution_fault(self, action_type: str, target: str, exception: Exception):
        """Register an exception to be thrown for a specific action and target."""
        self._faults[(action_type, target)] = ("EXECUTION", exception)
        logger.info(f"Fault injected for {action_type} -> {target} ({type(exception).__name__})")
        
    def inject_step_fault(self, objective_id: str, action_type: str, step_number: int,
                          exception: Exception, max_triggers: int = 1):
        """Register an exception to be thrown for a specific step of an objective.
        
        Args:
            objective_id: The objective this fault targets.
            action_type: The action_type string (e.g. 'CREATE_FILE_DIRECT').
            step_number: 0-based step index (matches context.current_step inside TaskExecutor).
            exception: The exception to raise when the step fires.
            max_triggers: How many times the fault will trigger before clearing itself.
                          Default 1 (single shot). Use -1 for unlimited (permanent fault).
        """
        self._faults[(objective_id, action_type, step_number)] = ("STEP", exception, max_triggers)
        logger.info(f"Step fault injected for {objective_id} step {step_number} ({type(exception).__name__}), max_triggers={max_triggers}")


        
    def inject_verification_fault(self, target: str):
        """Register a verification failure for a specific target."""
        self._faults[("VERIFICATION", target)] = ("VERIFICATION", None)
        logger.info(f"Verification fault injected for target: {target}")
        
    def check_execution_fault(self, action_type: str, target: str) -> Optional[Exception]:
        """Check if an execution fault is registered. If so, return and clear it."""
        key = (action_type, target)
        if key in self._faults and self._faults[key][0] == "EXECUTION":
            fault = self._faults.pop(key)[1]
            logger.warning(f"Triggering injected execution fault for {action_type} -> {target}")
            return fault
        return None
        
    def check_step_fault(self, context: 'ExecutionContext', action_type: str) -> Optional[Exception]:
        """Check if a step fault is registered for the current context."""
        if not context.objective_id:
            return None
            
        key = (context.objective_id, action_type, context.current_step)
        if key in self._faults and self._faults[key][0] == "STEP":
            entry = self._faults[key]
            fault = entry[1]
            max_triggers = entry[2] if len(entry) > 2 else 1
            
            if max_triggers == -1:
                # Permanent fault — never removed
                pass
            elif max_triggers <= 1:
                # Last allowed trigger — remove the fault
                del self._faults[key]
            else:
                # Decrement trigger count
                self._faults[key] = ("STEP", fault, max_triggers - 1)

            logger.warning(f"Triggering injected step fault for {context.objective_id} step {context.current_step}")
            return fault
        return None

        
    def check_verification_fault(self, target: str) -> bool:
        """Check if a verification fault is registered. If so, clear it and return True (indicating failure)."""
        key = ("VERIFICATION", target)
        if key in self._faults and self._faults[key][0] == "VERIFICATION":
            self._faults.pop(key)
            logger.warning(f"Triggering injected verification fault for target {target}")
            return True
        return False
        
    def clear(self):
        """Clear all injected faults (use between test cases to prevent leakage)."""
        self._faults.clear()

    @classmethod
    def reset(cls):
        """Destroy the singleton and clear all faults. Use in test teardown."""
        if cls._instance is not None:
            cls._instance._faults.clear()
            cls._instance = None

    def is_empty(self) -> bool:
        """Return True if no faults are currently registered."""
        return len(self._faults) == 0
