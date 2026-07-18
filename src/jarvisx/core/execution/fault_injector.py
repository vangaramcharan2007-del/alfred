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
        
    def check_verification_fault(self, target: str) -> bool:
        """Check if a verification fault is registered. If so, clear it and return True (indicating failure)."""
        key = ("VERIFICATION", target)
        if key in self._faults and self._faults[key][0] == "VERIFICATION":
            self._faults.pop(key)
            logger.warning(f"Triggering injected verification fault for target {target}")
            return True
        return False
        
    def clear(self):
        """Clear all injected faults."""
        self._faults.clear()
