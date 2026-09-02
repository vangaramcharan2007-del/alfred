from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class CapabilityHealthReport:
    capability_id: str
    status: str = "HEALTHY"
    heartbeat: float = field(default_factory=time.time)
    load_status: str = "LOADED"
    execution_failures: int = 0
    response_latency_ms: float = 0.0
    last_execution: float = 0.0
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "status": self.status,
            "heartbeat": round(self.heartbeat, 3),
            "load_status": self.load_status,
            "execution_failures": self.execution_failures,
            "response_latency_ms": round(self.response_latency_ms, 2),
            "last_execution": round(self.last_execution, 3),
            "version": self.version
        }

class CapabilityHealthMonitor:
    def __init__(self):
        self.reports: Dict[str, CapabilityHealthReport] = {}

    def register_capability(self, capability_id: str, version: str = "1.0.0") -> CapabilityHealthReport:
        report = CapabilityHealthReport(capability_id=capability_id, version=version)
        self.reports[capability_id] = report
        return report

    def record_heartbeat(self, capability_id: str) -> None:
        if capability_id in self.reports:
            self.reports[capability_id].heartbeat = time.time()

    def record_execution(self, capability_id: str, success: bool, latency_ms: float) -> None:
        if capability_id not in self.reports:
            self.register_capability(capability_id)
        
        report = self.reports[capability_id]
        report.last_execution = time.time()
        report.response_latency_ms = (report.response_latency_ms + latency_ms) / 2.0 if report.response_latency_ms > 0 else latency_ms
        
        if not success:
            report.execution_failures += 1
            if report.execution_failures >= 3:
                report.status = "DEGRADED"

    def get_report(self, capability_id: str) -> Optional[CapabilityHealthReport]:
        return self.reports.get(capability_id)

    def list_reports(self) -> List[CapabilityHealthReport]:
        return list(self.reports.values())
