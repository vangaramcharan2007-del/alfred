from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from jarvisx.engineering.impact_analyzer import ImpactAnalyzer, ImpactReport
from jarvisx.engineering.intelligence import ProjectIntelligence, RepositoryInfo


@dataclass
class EngineeringPlan:
    goal: str
    requirements: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    architecture_decisions: List[str] = field(default_factory=list)
    affected_modules: List[str] = field(default_factory=list)
    estimated_impact: str = "LOW"
    implementation_order: List[str] = field(default_factory=list)
    rollback_strategy: str = "Revert git working tree to baseline or restore atomic file backup checkpoints."
    risk_assessment: List[str] = field(default_factory=list)
    impact_reports: Dict[str, ImpactReport] = field(default_factory=dict)

    def generate_report(self) -> str:
        lines: List[str] = []
        lines.append(f"ENGINEERING PLAN: {self.goal}")
        lines.append("\nRequirements:")
        for r in self.requirements:
            lines.append(f"  - {r}")
        lines.append("\nAssumptions:")
        for a in self.assumptions:
            lines.append(f"  - {a}")
        lines.append("\nArchitecture Decisions:")
        for ad in self.architecture_decisions:
            lines.append(f"  - {ad}")
        lines.append("\nAffected Modules:")
        for mod in self.affected_modules:
            lines.append(f"  - {mod}")
        lines.append(f"\nEstimated Impact: {self.estimated_impact}")
        lines.append("\nImplementation Order:")
        for i, step in enumerate(self.implementation_order, 1):
            lines.append(f"  {i}. {step}")
        lines.append(f"\nRollback Strategy:\n  {self.rollback_strategy}")
        lines.append("\nRisk Assessment:")
        for rsk in self.risk_assessment:
            lines.append(f"  - {rsk}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "requirements": self.requirements,
            "assumptions": self.assumptions,
            "architecture_decisions": self.architecture_decisions,
            "affected_modules": self.affected_modules,
            "estimated_impact": self.estimated_impact,
            "implementation_order": self.implementation_order,
            "rollback_strategy": self.rollback_strategy,
            "risk_assessment": self.risk_assessment,
            "impact_reports": {k: v.to_dict() for k, v in self.impact_reports.items()},
        }


class ArchitectureReasoner:
    """
    Offline-first reasoning engine that formulates structured implementation blueprints,
    integrating runtime repository intelligence and automated impact analysis.
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        self.intel = ProjectIntelligence(self.repo_path)
        self.impact_analyzer = ImpactAnalyzer(self.repo_path)

    def plan_mission(self, goal: str, target_files: List[str] | None = None) -> EngineeringPlan:
        intel_report = self.intel.analyze()
        plan = EngineeringPlan(goal=goal)
        
        goal_lower = goal.lower()
        candidate_files: List[str] = target_files or []

        # Autonomously discover relevant candidate files based on mission semantic domain
        if not candidate_files:
            for filepath in intel_report.dependency_graph.keys():
                if "sqlite" in goal_lower or "postgresql" in goal_lower or "db" in goal_lower:
                    if any(w in filepath.lower() for w in ["db", "sql", "storage", "memory", "bridge"]):
                        candidate_files.append(filepath)
                elif "oauth" in goal_lower or "auth" in goal_lower or "login" in goal_lower:
                    if any(w in filepath.lower() for w in ["auth", "security", "api", "server", "login"]):
                        candidate_files.append(filepath)
                elif "docker" in goal_lower or "container" in goal_lower:
                    if any(w in filepath.lower() for w in ["docker", "deploy", "runtime"]):
                        candidate_files.append(filepath)
                elif "performance" in goal_lower or "improve" in goal_lower or "optimize" in goal_lower:
                    if any(w in filepath.lower() for w in ["runtime", "core", "agent", "memory", "cache"]):
                        candidate_files.append(filepath)
            
            # If no domain match, select top entry points or core runtime files
            if not candidate_files:
                candidate_files = [e for e in intel_report.entry_points if e.endswith(".py")][:3]
                if not candidate_files and intel_report.dependency_graph:
                    candidate_files = list(intel_report.dependency_graph.keys())[:2]

        candidate_files = list(set(candidate_files))[:5]
        plan.affected_modules = sorted(candidate_files)

        # Run Impact Analysis on all affected modules
        highest_impact = "LOW"
        risk_weights = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        for mod in plan.affected_modules:
            report = self.impact_analyzer.analyze_file(mod)
            plan.impact_reports[mod] = report
            if risk_weights[report.estimated_regression_risk] > risk_weights[highest_impact]:
                highest_impact = report.estimated_regression_risk
            for ev in report.supporting_evidence:
                plan.risk_assessment.append(f"[{mod}] {ev}")

        plan.estimated_impact = highest_impact

        # Reason over domain logic for structured plan generation
        if "sqlite" in goal_lower and "postgresql" in goal_lower:
            plan.requirements = [
                "Implement scalable PostgreSQL database connection pooling and schema compatibility interfaces.",
                "Maintain complete fallback compatibility for local offline execution without breaking existing SQLite callers.",
                "Ensure all active unit test suites execute cleanly across both storage backends.",
            ]
            plan.assumptions = [
                "Target runtime environments provide either a reachable PostgreSQL DSN via environment variables or require an emulated SQLite abstraction.",
                "Existing data processing contracts depend on standard SQL query execution semantics.",
            ]
            plan.architecture_decisions = [
                "Adopt an abstract Database Engine adapter pattern (e.g., in db_bridge.py or operational_db.py) to encapsulate driver-specific dialect variance.",
                "Enforce lazy driver initialization so offline test executions operate without requiring external PostgreSQL server sockets.",
            ]
            plan.implementation_order = [
                "Analyze existing database connection setup and query construction patterns.",
                "Introduce PostgreSQL connection capabilities with graceful import fallback.",
                "Extend unit tests to validate abstraction contract compliance.",
            ]
            plan.rollback_strategy = "Revert modified database engine adapter files; restore prior atomic connection factory logic."

        elif "docker" in goal_lower or "container" in goal_lower:
            plan.requirements = [
                "Define multi-stage Docker container build specifications optimized for production footprint reduction.",
                "Expose required environment configuration bindings and networking ports cleanly.",
            ]
            plan.assumptions = [
                f"Repository utilizes {intel_report.package_manager} as its primary dependency management framework.",
            ]
            plan.architecture_decisions = [
                "Utilize multi-stage container build architecture to separate compiling/dev dependencies from operational runtime artifacts.",
            ]
            plan.implementation_order = [
                "Verify or generate standalone Dockerfile with hardened entrypoint script execution.",
                "Validate syntax and check configuration compatibility against compose specifications.",
            ]
            plan.rollback_strategy = "Remove generated Docker artifacts and restore prior environment configuration files."

        elif "oauth" in goal_lower or "login" in goal_lower:
            plan.requirements = [
                "Implement secure OAuth 2.0 / Token authentication validation endpoints in API server layer.",
                "Protect sensitive execution routes against unauthenticated remote invocations.",
            ]
            plan.assumptions = [
                "API requests arrive over standard REST / ASGI transport interfaces.",
            ]
            plan.architecture_decisions = [
                "Integrate modular dependency injection middleware for JWT token verification without mutating domain worker logic.",
            ]
            plan.implementation_order = [
                "Construct security authentication validation schema and helper utilities.",
                "Wrap target REST endpoint controllers with authentication enforcement decorators.",
            ]
            plan.rollback_strategy = "Remove middleware decorator wrappers from API routing bindings."

        elif "recommend" in goal_lower and "improvements" in goal_lower:
            top_imps = intel_report.improvement_opportunities[:3]
            plan.requirements = [f"Evaluate and prepare implementation blueprints for: {imp}" for imp in top_imps]
            plan.assumptions = ["Repository architecture requires continuous proactive maintenance and resilience hardening."]
            plan.architecture_decisions = ["Prioritize improvements addressing high-concurrency bottlenecking and CI validation stability."]
            plan.implementation_order = [
                "Rank identified repository risk areas by systemic severity.",
                "Draft architectural corrective action proposals for the top 3 items.",
            ]
        else:
            plan.requirements = [
                f"Execute goal: '{goal}' in accordance with rigorous offline-first reliability standards.",
                "Ensure zero regression across existing automated test suites.",
            ]
            plan.assumptions = [
                f"Target repository follows a {intel_report.architecture_style} pattern.",
            ]
            plan.architecture_decisions = [
                "Minimize public API signature mutation; isolate modifications to modular implementation internals.",
            ]
            plan.implementation_order = [
                "Perform target module inspection and abstract AST interface mapping.",
                "Apply atomic file refactoring and structural updates.",
                "Execute test suite verification and initiate automated debug healing if necessary.",
            ]

        if not plan.risk_assessment:
            plan.risk_assessment.append("No critical architectural risks flagged by downstream dependency analysis.")

        return plan
