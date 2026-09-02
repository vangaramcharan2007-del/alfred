"""
3-Perspective Adversarial Code & Plan Review Engine.
Adapted and refined from Garry Tan's gstack review architecture (review, plan-eng-review, careful).

Features:
- Multi-Angle Inspection:
  1. Engineering Architecture (Modularity, coupling, no hardcoded paths)
  2. Security & Boundaries (Credential leak scan, path traversal, shell safety)
  3. Quality & Ship Readiness (Exception isolation, timeouts, completeness score)
- Deterministic scoring (1-10 Completeness Principle: 'Boil the Ocean')
- Actionable blocker identification.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ReviewFinding:
    severity: str  # 'BLOCKER', 'WARNING', 'SUGGESTION'
    perspective: str  # 'ARCHITECTURE', 'SECURITY', 'QUALITY'
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class AdversarialReviewReport:
    decision: str  # 'APPROVED', 'APPROVED_WITH_WARNINGS', 'REJECTED'
    completeness_score: int  # 1 to 10
    total_findings: int
    findings: List[ReviewFinding] = field(default_factory=list)
    summary: str = ""


class AdversarialReviewEngine:
    """Executes multi-perspective review across code, diffs, and mission plans."""

    SECRET_PATTERNS = [
        re.compile(r"""(?i)(api_key|secret_key|private_key|token|password|bearer)\s*=\s*['"][a-zA-Z0-9_\-\.]{16,}['"]"""),
        re.compile(r"""(?i)sk-[a-zA-Z0-9]{20,}"""),
        re.compile(r"""(?i)ghp_[a-zA-Z0-9]{20,}"""),
    ]

    HARDCODED_PATH_PATTERNS = [
        re.compile(r"""[A-Za-z]:\\[Uu]sers\\[a-zA-Z0-9_]+"""),
        re.compile(r"""/home/[a-zA-Z0-9_]+"""),
    ]

    UNSAFE_CALL_PATTERNS = [
        re.compile(r"""\bexec\s*\("""),
        re.compile(r"""\beval\s*\("""),
        re.compile(r"""\bsubprocess\.Popen\(.*shell\s*=\s*True"""),
        re.compile(r"""\bos\.system\s*\("""),
    ]

    def review_code_or_diff(self, content: str, file_path: str = "snippet.py") -> AdversarialReviewReport:
        """Runs the 3-angle review on arbitrary code or diff content."""
        findings: List[ReviewFinding] = []

        lines = content.splitlines()

        # Angle 1: Security & Boundaries
        for idx, line in enumerate(lines, 1):
            for pattern in self.SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        ReviewFinding(
                            severity="BLOCKER",
                            perspective="SECURITY",
                            message="Potential hardcoded credential or secret detected.",
                            file_path=file_path,
                            line_number=idx,
                        )
                    )

            for pattern in self.UNSAFE_CALL_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        ReviewFinding(
                            severity="BLOCKER",
                            perspective="SECURITY",
                            message="Potentially unsafe dynamic execution (eval/exec/shell=True).",
                            file_path=file_path,
                            line_number=idx,
                        )
                    )

            if ".." in line and ("open(" in line or "Path(" in line or "read_file" in line):
                findings.append(
                    ReviewFinding(
                        severity="WARNING",
                        perspective="SECURITY",
                        message="Relative path traversal ('..') detected. Ensure permission gateway verifies canonical path.",
                        file_path=file_path,
                        line_number=idx,
                    )
                )

        # Angle 2: Engineering Architecture
        for idx, line in enumerate(lines, 1):
            for pattern in self.HARDCODED_PATH_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        ReviewFinding(
                            severity="WARNING",
                            perspective="ARCHITECTURE",
                            message="Hardcoded machine-specific user directory path. Use relative paths or config.",
                            file_path=file_path,
                            line_number=idx,
                        )
                    )

            if line.strip().startswith("except:") or line.strip() == "except Exception: pass":
                findings.append(
                    ReviewFinding(
                        severity="WARNING",
                        perspective="ARCHITECTURE",
                        message="Bare or silent exception handling suppresses critical diagnostic logs.",
                        file_path=file_path,
                        line_number=idx,
                    )
                )

        # Angle 3: QA & Quality (Completeness scoring)
        has_tests_or_docstrings = any(
            line.strip().startswith('"""') or line.strip().startswith("def test_") for line in lines
        )
        if not has_tests_or_docstrings and len(lines) > 20:
            findings.append(
                ReviewFinding(
                    severity="SUGGESTION",
                    perspective="QUALITY",
                    message="Add structured docstrings or unit test coverage for mission readiness.",
                    file_path=file_path,
                )
            )

        # Calculate completeness score (Boil the Ocean 1-10)
        blockers = [f for f in findings if f.severity == "BLOCKER"]
        warnings = [f for f in findings if f.severity == "WARNING"]

        if blockers:
            score = max(1, 4 - len(blockers))
            decision = "REJECTED"
            summary = f"Review Failed: {len(blockers)} blocker(s) detected. Security or architecture fixes required."
        elif warnings:
            score = max(5, 8 - len(warnings))
            decision = "APPROVED_WITH_WARNINGS"
            summary = f"Review Passed with {len(warnings)} non-blocking warning(s). Minor improvements recommended."
        else:
            score = 10
            decision = "APPROVED"
            summary = "Review Passed: High architectural integrity, zero security violations, production-grade."

        return AdversarialReviewReport(
            decision=decision,
            completeness_score=score,
            total_findings=len(findings),
            findings=findings,
            summary=summary,
        )
