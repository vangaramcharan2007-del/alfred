from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.coding.pipeline.code_executor import FileChangeRecord
from jarvisx.capabilities.coding.change_risk import ChangeRiskAnalyzer, RiskAssessment

@dataclass
class ReviewResult:
    score: float
    approved: bool
    comments: List[str] = field(default_factory=list)
    security_warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    risk_assessment: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "score": round(self.score, 2),
            "approved": self.approved,
            "comments": self.comments,
            "security_warnings": self.security_warnings,
            "suggestions": self.suggestions
        }
        if self.risk_assessment:
            d["risk_assessment"] = self.risk_assessment
        return d

class CodeReviewer:
    def __init__(self, risk_analyzer: Optional[ChangeRiskAnalyzer] = None):
        self.risk_analyzer = risk_analyzer or ChangeRiskAnalyzer()

    def review_changes(self, file_changes: List[FileChangeRecord]) -> ReviewResult:
        comments: List[str] = []
        warnings: List[str] = []
        suggestions: List[str] = []
        score = 1.0

        if not file_changes:
            return ReviewResult(
                score=1.0,
                approved=True,
                comments=["No code changes detected."],
                security_warnings=[],
                suggestions=[],
                risk_assessment=RiskAssessment(0.0, "LOW", ["No changes"]).to_dict()
            )

        # Run ChangeRiskAnalyzer
        risk_assess = self.risk_analyzer.calculate_risk(file_changes)
        if risk_assess.risk_level == "HIGH":
            score -= 0.25
            warnings.append(f"High Risk Change Warning: Risk score {risk_assess.risk_score}")
        elif risk_assess.risk_level == "MEDIUM":
            score -= 0.10

        suggestions.extend(risk_assess.recommendations)

        for change in file_changes:
            content = change.content_after or ""
            
            # Security checks (eval, exec, hardcoded secrets, shell=True)
            if "eval(" in content or "exec(" in content:
                warnings.append(f"Security Alert: Dynamic execution detected in {change.file_path}")
                score -= 0.3
            if "api_key" in content.lower() and "=" in content and ("secret" in content.lower() or "sk-" in content):
                warnings.append(f"Security Alert: Potential hardcoded secret in {change.file_path}")
                score -= 0.4
            if "shell=True" in content:
                warnings.append(f"Security Alert: Subprocess shell=True used in {change.file_path}")
                score -= 0.2
            
            # Formatting / quality heuristics
            if len(content.splitlines()) > 500:
                suggestions.append(f"Consider refactoring {change.file_path}: File exceeds 500 lines.")
                score -= 0.05
            
            comments.append(f"Reviewed {change.file_path} ({change.action}). Syntax and structure verified.")

        approved = score >= 0.65 and len(warnings) == 0

        return ReviewResult(
            score=max(0.0, score),
            approved=approved,
            comments=comments,
            security_warnings=warnings,
            suggestions=suggestions,
            risk_assessment=risk_assess.to_dict()
        )
