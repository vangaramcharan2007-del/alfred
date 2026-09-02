"""Execution Monitor for Jarvis X (Layer 3 - Execution).

Tracks execution metrics: duration, failure count, retries, RAM/CPU resource usage, and completion quality.
"""

import os
import psutil
from typing import Any, Dict, List, Optional


class ExecutionMonitor:
    """Zero-fluff production execution monitoring engine."""

    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []

    def record_execution_telemetry(
        self,
        mission_id: str,
        title: str,
        status: str,
        duration_seconds: float,
        retry_count: int = 0,
        quality_score: float = 1.0,
    ) -> Dict[str, Any]:
        """Record process telemetry and execution statistics."""
        process = psutil.Process(os.getpid())
        ram_mb = round(process.memory_info().rss / (1024 * 1024), 2)
        cpu_pct = round(process.cpu_percent(interval=0.05), 2)

        entry = {
            "mission_id": mission_id,
            "title": title,
            "status": status,
            "duration_seconds": round(duration_seconds, 3),
            "retry_count": retry_count,
            "ram_usage_mb": ram_mb,
            "cpu_percent": cpu_pct,
            "quality_score": max(0.0, min(1.0, quality_score)),
        }
        self.metrics_history.append(entry)
        return entry

    def get_performance_summary(self) -> Dict[str, Any]:
        """Synthesize overall execution performance telemetry."""
        total = len(self.metrics_history)
        if total == 0:
            return {"status": "nominal", "total_executions": 0, "avg_duration": 0.0, "success_rate": 1.0}

        successes = sum(1 for m in self.metrics_history if m["status"] == "COMPLETED")
        avg_dur = sum(m["duration_seconds"] for m in self.metrics_history) / total
        avg_quality = sum(m["quality_score"] for m in self.metrics_history) / total

        return {
            "status": "nominal",
            "total_executions": total,
            "successful_executions": successes,
            "success_rate": round(successes / total, 2),
            "avg_duration": round(avg_dur, 3),
            "avg_quality_score": round(avg_quality, 2),
            "recent_metrics": self.metrics_history[-5:],
        }
