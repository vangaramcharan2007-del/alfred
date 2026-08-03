import pytest
from jarvisx.capabilities.coding.pipeline.code_executor import FileChangeRecord
from jarvisx.capabilities.github.github_review import GitHubReviewIntelligence

@pytest.mark.asyncio
async def test_github_review_intelligence():
    intel = GitHubReviewIntelligence()
    changes = [
        FileChangeRecord(
            file_path="src/auth.py",
            action="modified",
            content_after="def login(): pass\nfor i in range(10):\n  for j in range(10): pass\n"
        )
    ]

    report = await intel.generate_comprehensive_review(file_changes=changes, idea_description="Build Auth Module")

    assert "score" in report
    assert "security_review" in report
    assert "risk_review" in report
    assert "missing_tests_check" in report
    assert len(report["performance_concerns"]) >= 1
