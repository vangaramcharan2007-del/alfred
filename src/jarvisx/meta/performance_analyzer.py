from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.meta.performance_monitor import PerformanceMonitor

class PerformanceAnalyzer:
    def __init__(self, monitor: Optional[PerformanceMonitor] = None):
        self.monitor = monitor or PerformanceMonitor()

    def detect_degraded_capabilities(self, threshold: float = 0.85) -> List[Dict[str, Any]]:
        summary = self.monitor.get_performance_summary()
        degraded = []
        for cap_id, stats in summary.items():
            if stats["success_rate"] < threshold:
                degraded.append({
                    "capability_id": cap_id,
                    "success_rate": stats["success_rate"],
                    "threshold": threshold,
                    "issue": f"Success rate ({stats['success_rate']*100}%) below threshold ({threshold*100}%)"
                })
        return degraded
