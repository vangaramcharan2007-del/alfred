from typing import List
from jarvisx.core.failure_monitor import FailureMonitor

class CapabilityGapAnalyzer:
    """Owns root cause analysis of failures."""
    
    def __init__(self, failure_monitor: FailureMonitor):
        self.monitor = failure_monitor
        self.gap_threshold = 3
        
    def detect_capability_gaps(self) -> List[str]:
        """Detect repeated missing capabilities."""
        failures = self.monitor.get_all_failures()
        gaps = []
        for capability, data in failures.items():
            if data["failure_count"] >= self.gap_threshold:
                # Basic mapping for demo purposes. 
                # If capability is missing _missing, we extract the base name.
                base_cap = capability.replace("_missing", "")
                if base_cap not in gaps:
                    gaps.append(base_cap)
        return gaps
        
    def generate_gap_report(self) -> str:
        """Generate capability gap reports."""
        gaps = self.detect_capability_gaps()
        if not gaps:
            return "No capability gaps detected."
            
        report = "Capability Gap Detected:\n\n"
        for gap in gaps:
            report += f"{gap}\n"
        return report.strip()
