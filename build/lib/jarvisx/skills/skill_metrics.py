"""Skill Performance Tracking and Metrics for Phase 92.5 Capability Intelligence Layer."""

from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional


class SkillMetricsTracker:
    """Tracks times used, success rates, average execution latency, and failure counts."""

    def __init__(self, metrics_file: str = "var/skills/metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.load_metrics()

    def load_metrics(self) -> None:
        if self.metrics_file.exists():
            try:
                self.metrics = json.loads(self.metrics_file.read_text(encoding="utf-8"))
            except Exception:
                self.metrics = {}
        else:
            self.metrics = {}

    def save_metrics(self) -> None:
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_file.write_text(json.dumps(self.metrics, indent=2), encoding="utf-8")

    def record_usage(self, skill_name: str, success: bool, duration_sec: float) -> Dict[str, Any]:
        """Record execution outcome, latency, and update running success rate."""
        if skill_name not in self.metrics:
            self.metrics[skill_name] = {
                "times_used": 0,
                "successful_uses": 0,
                "failures": 0,
                "success_rate": 1.0,
                "total_duration_sec": 0.0,
                "average_runtime_sec": 0.0,
                "last_used": 0.0
            }

        rec = self.metrics[skill_name]
        rec["times_used"] += 1
        if success:
            rec["successful_uses"] += 1
        else:
            rec["failures"] += 1

        rec["total_duration_sec"] += duration_sec
        rec["average_runtime_sec"] = round(rec["total_duration_sec"] / rec["times_used"], 3)
        rec["success_rate"] = round(rec["successful_uses"] / rec["times_used"], 2)
        rec["last_used"] = time.time()

        self.save_metrics()
        return rec

    def get_skill_stats(self, skill_name: str) -> Optional[Dict[str, Any]]:
        return self.metrics.get(skill_name)
