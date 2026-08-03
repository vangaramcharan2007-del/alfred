from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.meta.capability_introspection import CapabilityIntrospector
from jarvisx.meta.performance_monitor import PerformanceMonitor

class EnhancedDecisionEngine:
    def __init__(
        self,
        introspector: Optional[CapabilityIntrospector] = None,
        performance_monitor: Optional[PerformanceMonitor] = None
    ):
        self.introspector = introspector or CapabilityIntrospector()
        self.perf_monitor = performance_monitor or PerformanceMonitor()

    def evaluate_task_execution(self, task_description: str) -> Dict[str, Any]:
        analysis = self.introspector.analyze_mission(task_description)
        missing = analysis.get("missing_capabilities", [])
        sufficiency = analysis.get("sufficiency_score", 1.0)

        knowledge_gap_score = round(len(missing) * 0.25, 2)
        self_awareness_score = 0.95
        capability_confidence = round(max(0.1, min(1.0, sufficiency - knowledge_gap_score)), 2)

        can_proceed = capability_confidence >= 0.50

        return {
            "task": task_description,
            "self_awareness_score": self_awareness_score,
            "capability_confidence": capability_confidence,
            "knowledge_gap_score": knowledge_gap_score,
            "can_proceed": can_proceed,
            "missing_capabilities": missing,
            "recommendations": analysis.get("recommendations", [])
        }
