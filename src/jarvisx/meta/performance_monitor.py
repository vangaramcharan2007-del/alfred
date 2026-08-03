from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.coding.metrics import CodingMetrics

class PerformanceMonitor:
    def __init__(self, metrics: Optional[CodingMetrics] = None):
        self.metrics = metrics or CodingMetrics()
        self.capability_runs: Dict[str, Dict[str, Any]] = {}

    def record_capability_run(
        self,
        capability_id: str,
        success: bool,
        duration_seconds: float,
        tokens_used: int = 0
    ) -> None:
        if capability_id not in self.capability_runs:
            self.capability_runs[capability_id] = {
                "total_runs": 0,
                "successful_runs": 0,
                "total_duration": 0.0,
                "total_tokens": 0
            }
        stats = self.capability_runs[capability_id]
        stats["total_runs"] += 1
        if success:
            stats["successful_runs"] += 1
        stats["total_duration"] += duration_seconds
        stats["total_tokens"] += tokens_used

    def get_performance_summary(self) -> Dict[str, Any]:

        summary: Dict[str, Any] = {}
        for cap_id, stats in self.capability_runs.items():
            total = stats["total_runs"]
            succ = stats["successful_runs"]
            rate = round(succ / total, 3) if total > 0 else 1.0
            avg_dur = round(stats["total_duration"] / total, 3) if total > 0 else 0.0
            summary[cap_id] = {
                "total_runs": total,
                "success_rate": rate,
                "average_duration": avg_dur,
                "total_tokens": stats["total_tokens"]
            }
        return summary
