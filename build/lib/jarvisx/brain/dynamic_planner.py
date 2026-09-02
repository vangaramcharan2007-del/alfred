"""
Dynamic Task Planner for Alfred & Friday.
Decomposes any unknown natural language objective into structured atomic tasks,
detects tool dependencies, and classifies security risk levels.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.core.capability_discovery import CapabilityDiscoverySystem, MatchResult
from jarvisx.core.safety import ProductionSafetyGate, RiskLevel


@dataclass
class AtomicTask:
    task_id: str
    description: str
    capability_matched: MatchResult
    dependencies: List[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    requires_approval: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "capability": self.capability_matched.to_dict(),
            "dependencies": self.dependencies,
            "risk_level": self.risk_level.value,
            "requires_approval": self.requires_approval
        }


@dataclass
class ExecutionPlan:
    objective: str
    understanding: str
    tasks: List[AtomicTask]
    estimated_risk: RiskLevel

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective": self.objective,
            "understanding": self.understanding,
            "tasks": [t.to_dict() for t in self.tasks],
            "estimated_risk": self.estimated_risk.value
        }


class DynamicTaskPlanner:
    """Decomposes arbitrary natural language objectives into executable task plans."""

    def __init__(self, discovery_system: Optional[CapabilityDiscoverySystem] = None):
        self.discovery = discovery_system or CapabilityDiscoverySystem()

    def generate_plan(self, objective: str) -> ExecutionPlan:
        obj_lower = objective.lower()
        understanding = f"Objective identified: '{objective}'. Synthesizing atomic steps, capabilities, and dependencies."
        atomic_tasks: List[AtomicTask] = []

        # Generic intelligent decomposition rules based on intent
        if any(w in obj_lower for w in ["tracker", "expense", "app", "application", "system", "script"]):
            steps_data = [
                ("Analyze requirements and design project structure", "tool.file_system"),
                ("Create module source files and configuration", "tool.file_system"),
                ("Implement business logic and execution functions", "tool.python_executor"),
                ("Execute application and run test suite", "tool.python_executor"),
                ("Review execution output and store in memory", "tool.memory")
            ]
        elif any(w in obj_lower for w in ["study", "plan", "revision", "academic", "operating systems", "cgpa", "exam"]):
            steps_data = [
                ("Load academic profile and subject credit breakdown", "tool.academic_engine"),
                ("Calculate 10 CGPA subject priority scores", "tool.academic_engine"),
                ("Generate actionable study timetable schedule", "tool.academic_engine"),
                ("Log study targets to memory", "tool.memory")
            ]
        elif any(w in obj_lower for w in ["pdf", "ocr", "read"]):
            steps_data = [
                ("Identify target document file", "tool.file_system"),
                ("Extract document text using OCR / parser", "tool.ocr_vision"),
                ("Summarize document insights and store memory", "tool.memory")
            ]
        else:
            steps_data = [
                ("Analyze goal requirements", "tool.file_system"),
                ("Execute core solution script", "tool.python_executor"),
                ("Verify execution output", "tool.python_executor"),
                ("Store task summary in memory", "tool.memory")
            ]

        max_risk = RiskLevel.LOW

        for idx, (desc, cap_hint) in enumerate(steps_data, start=1):
            task_id = f"T{idx:02d}"
            cap_match = self.discovery.discover_best_capability(desc)
            risk = ProductionSafetyGate.classify_risk(desc)
            requires_appr = risk in (RiskLevel.HIGH, RiskLevel.CRITICAL)

            if risk == RiskLevel.HIGH and max_risk != RiskLevel.CRITICAL:
                max_risk = RiskLevel.HIGH
            elif risk == RiskLevel.CRITICAL:
                max_risk = RiskLevel.CRITICAL

            deps = [f"T{idx-1:02d}"] if idx > 1 else []

            atomic_tasks.append(AtomicTask(
                task_id=task_id,
                description=desc,
                capability_matched=cap_match,
                dependencies=deps,
                risk_level=risk,
                requires_approval=requires_appr
            ))

        return ExecutionPlan(
            objective=objective,
            understanding=understanding,
            tasks=atomic_tasks,
            estimated_risk=max_risk
        )
