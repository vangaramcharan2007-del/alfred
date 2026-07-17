import time
from typing import Dict, Any

class FailureMonitor:
    """Owns failure aggregation."""
    
    def __init__(self):
        self._failures: Dict[str, Dict[str, Any]] = {}
        
    def record_failure(self, capability: str):
        """Record a failure for a specific capability."""
        if capability not in self._failures:
            self._failures[capability] = {
                "failure_count": 0,
                "last_failure": ""
            }
            
        self._failures[capability]["failure_count"] += 1
        self._failures[capability]["last_failure"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        
    def get_failure_count(self, capability: str) -> int:
        """Get the number of failures for a capability."""
        if capability in self._failures:
            return self._failures[capability]["failure_count"]
        return 0
        
    def get_all_failures(self) -> Dict[str, Dict[str, Any]]:
        """Return all tracked failures."""
        return self._failures
        
    def clear_failures(self, capability: str):
        """Clear failures for a capability."""
        if capability in self._failures:
            del self._failures[capability]
