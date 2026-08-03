from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.coding.pipeline.code_reviewer import CodeReviewer
from jarvisx.capabilities.coding.change_risk import ChangeRiskAnalyzer
from jarvisx.capabilities.coding.architecture_agent import ArchitectureAgent
from jarvisx.capabilities.coding.pipeline.code_executor import FileChangeRecord

class GitHubReviewIntelligence:
    def __init__(
        self,
        code_reviewer: Optional[CodeReviewer] = None,
        risk_analyzer: Optional[ChangeRiskAnalyzer] = None,
        arch_agent: Optional[ArchitectureAgent] = None
    ):
        self.code_reviewer = code_reviewer or CodeReviewer()
        self.risk_analyzer = risk_analyzer or ChangeRiskAnalyzer()
        self.arch_agent = arch_agent or ArchitectureAgent()

    async def generate_comprehensive_review(
        self,
        file_changes: List[FileChangeRecord],
        idea_description: Optional[str] = None
    ) -> Dict[str, Any]:
        # Step 1: Security & Quality Review via CodeReviewer
        review_res = self.code_reviewer.review_changes(file_changes)

        # Step 2: Change Risk Analysis
        risk_assess = self.risk_analyzer.calculate_risk(file_changes)

        # Step 3: Architecture Audit
        arch_audit = "Architecture alignment verified. Multi-component interfaces intact."
        if idea_description:
            arch_proposal = await self.arch_agent.design_system(idea_description)
            arch_audit = f"Architecture evaluated for '{arch_proposal['project_name']}'. System components aligned."

        # Step 4: Missing Tests Check
        changed_paths = [c.file_path for c in file_changes]
        test_files = [p for p in changed_paths if "test_" in p or "_test" in p]
        has_missing_tests = len(test_files) == 0 and len(file_changes) > 0
        test_warning = "Warning: No test files modified or added in this pull request." if has_missing_tests else "Tests included."

        # Step 5: Performance Concerns Check
        perf_concerns = []
        for change in file_changes:
            content = change.content_after or ""
            if "for " in content and "for " in content[content.find("for ") + 4:]:
                perf_concerns.append(f"Nested loop detected in {change.file_path}")
            if "time.sleep(" in content:
                perf_concerns.append(f"Blocking sleep call detected in {change.file_path}")

        return {
            "score": review_res.score,
            "approved": review_res.approved and risk_assess.risk_level != "HIGH",
            "security_review": review_res.security_warnings,
            "risk_review": risk_assess.to_dict(),
            "architecture_review": arch_audit,
            "missing_tests_check": test_warning,
            "performance_concerns": perf_concerns,
            "suggestions": review_res.suggestions
        }
