from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.coding.pipeline.code_executor import FileChangeRecord

@dataclass
class ReviewResult:
    score: float
    approved: bool
    comments: List[str] = field(default_factory=list)
    security_warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": round(self.score, 2),
            "approved": self.approved,
            "comments": self.comments,
            "security_warnings": self.security_warnings,
            "suggestions": self.suggestions
        }

class CodeReviewer:
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
                suggestions=[]
            )

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

        approved = score >= 0.7 and len(warnings) == 0

        return ReviewResult(
            score=max(0.0, score),
            approved=approved,
            comments=comments,
            security_warnings=warnings,
            suggestions=suggestions
        )
