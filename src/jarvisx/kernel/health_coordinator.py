from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.kernel.subsystem_manager import SubsystemManager

class HealthCoordinator:
    def __init__(self, subsystem_manager: Optional[SubsystemManager] = None):
        self.subsystem_mgr = subsystem_manager or SubsystemManager()

    def run_health_check(self) -> Dict[str, Any]:
        statuses = self.subsystem_mgr.get_all_statuses()
        total = len(statuses)
        online = sum(1 for s in statuses if s["status"] == "ONLINE")
        degraded = self.subsystem_mgr.get_degraded()

        health_score = round(online / total, 2) if total > 0 else 0.0

        return {
            "total_subsystems": total,
            "online": online,
            "degraded_count": len(degraded),
            "degraded_subsystems": degraded,
            "health_score": health_score,
            "overall": "HEALTHY" if health_score >= 0.90 else "DEGRADED" if health_score >= 0.50 else "CRITICAL",
            "subsystems": statuses
        }
