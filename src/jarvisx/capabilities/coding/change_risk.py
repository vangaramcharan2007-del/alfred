from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.coding.pipeline.code_executor import FileChangeRecord
from jarvisx.capabilities.coding.dependency_analyzer import DependencyAnalyzer, ImpactReport

@dataclass
class RiskAssessment:
    risk_score: float
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    risk_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_score": round(self.risk_score, 2),
            "risk_level": self.risk_level,
            "risk_factors": self.risk_factors,
            "recommendations": self.recommendations
        }

class ChangeRiskAnalyzer:
    def __init__(self, dependency_analyzer: Optional[DependencyAnalyzer] = None):
        self.dep_analyzer = dependency_analyzer or DependencyAnalyzer()

    def calculate_risk(
        self,
        file_changes: List[FileChangeRecord],
        impact_report: Optional[ImpactReport] = None
    ) -> RiskAssessment:
        factors: List[str] = []
        recommendations: List[str] = []
        base_score = 0.1

        if not file_changes:
            return RiskAssessment(
                risk_score=0.0,
                risk_level="LOW",
                risk_factors=["No file changes detected."],
                recommendations=["No actions required."]
            )

        target_paths = [fc.file_path for fc in file_changes]

        # Use impact report if provided or calculate
        if impact_report is None:
            impact_report = self.dep_analyzer.analyze_impact(target_paths)

        affected_count = len(impact_report.affected_files)
        if affected_count >= 5:
            base_score += 0.35
            factors.append(f"Broad impact: {affected_count} downstream files affected.")
        elif affected_count >= 2:
            base_score += 0.15
            factors.append(f"Moderate impact: {affected_count} downstream files affected.")

        # Check core module modifications
        for fc in file_changes:
            fp_lower = fc.file_path.lower()
            if any(keyword in fp_lower for keyword in ["auth", "db", "security", "schema", "user", "password"]):
                base_score += 0.30
                factors.append(f"Core sensitive module modified: {fc.file_path}")
                recommendations.append(f"Perform rigorous security audit and regression testing on {fc.file_path}.")

            content = fc.content_after or ""
            if "eval(" in content or "exec(" in content or "shell=True" in content:
                base_score += 0.40
                factors.append(f"High risk dynamic code execution / process shell in {fc.file_path}")
                recommendations.append(f"Eliminate dynamic execution in {fc.file_path}.")

            if "api_key" in content.lower() and "=" in content:
                base_score += 0.25
                factors.append(f"Potential sensitive credential string in {fc.file_path}")

        # Check missing test coverage
        has_tests = any("test" in f.lower() for f in impact_report.affected_files)
        if not has_tests:
            base_score += 0.15
            factors.append("No automated test files detected covering modified components.")
            recommendations.append("Add unit tests to validate modified components.")

        final_score = min(1.0, max(0.0, base_score))
        if final_score >= 0.65:
            risk_level = "HIGH"
        elif final_score >= 0.35:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return RiskAssessment(
            risk_score=final_score,
            risk_level=risk_level,
            risk_factors=factors,
            recommendations=recommendations
        )
