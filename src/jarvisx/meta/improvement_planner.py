from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.meta.performance_analyzer import PerformanceAnalyzer
from jarvisx.meta.failure_analyzer import FailureAnalyzer

@dataclass
class ImprovementMission:
    mission_id: str
    title: str
    problem_statement: str
    priority: int
    action_items: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "title": self.title,
            "problem_statement": self.problem_statement,
            "priority": self.priority,
            "action_items": self.action_items
        }

class ImprovementPlanner:
    def __init__(
        self,
        performance_analyzer: Optional[PerformanceAnalyzer] = None,
        failure_analyzer: Optional[FailureAnalyzer] = None
    ):
        self.perf_analyzer = performance_analyzer or PerformanceAnalyzer()
        self.fail_analyzer = failure_analyzer or FailureAnalyzer()

    def generate_improvement_plan(self) -> List[ImprovementMission]:
        missions: List[ImprovementMission] = []

        # 1. Analyze degraded capabilities
        degraded = self.perf_analyzer.detect_degraded_capabilities()
        for deg in degraded:
            mid = f"imp_{uuid.uuid4().hex[:6]}"
            missions.append(ImprovementMission(
                mission_id=mid,
                title=f"Upgrade capability: {deg['capability_id']}",
                problem_statement=deg["issue"],
                priority=1,
                action_items=[
                    f"Profile capability {deg['capability_id']} bottlenecks",
                    "Add dedicated AST parser or language-specific MCP tool",
                    "Update model routing profiles"
                ]
            ))

        # 2. Analyze failure patterns
        patterns = self.fail_analyzer.analyze_patterns()
        for pat in patterns:
            mid = f"imp_{uuid.uuid4().hex[:6]}"
            missions.append(ImprovementMission(
                mission_id=mid,
                title=f"Mitigate provider failures: {pat['provider_id']}",
                problem_statement=pat["insight"],
                priority=2,
                action_items=[
                    f"Adjust ProviderSelector scoring penalty for {pat['provider_id']}",
                    "Enable automatic fallback routing upon task initiation"
                ]
            ))

        if not missions:
            # Default proactive system maintenance plan
            mid = f"imp_{uuid.uuid4().hex[:6]}"
            missions.append(ImprovementMission(
                mission_id=mid,
                title="System Optimization & Capability Audit",
                problem_statement="Routine self-improvement scan: no critical degradation detected.",
                priority=3,
                action_items=["Audit registered MCP servers", "Benchmark local Ollama inference latencies"]
            ))

        missions.sort(key=lambda m: m.priority)
        return missions
