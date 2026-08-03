import pytest
from jarvisx.capabilities.coding.pipeline.code_executor import FileChangeRecord
from jarvisx.capabilities.coding.pipeline.code_reviewer import CodeReviewer

def test_code_reviewer_clean():
    reviewer = CodeReviewer()
    changes = [
        FileChangeRecord(
            file_path="main.py",
            action="modified",
            content_before="",
            content_after="def add(a: float, b: float) -> float:\n    return a + b\n"
        )
    ]
    res = reviewer.review_changes(changes)
    assert res.approved is True
    assert res.score >= 0.9
    assert len(res.security_warnings) == 0

def test_code_reviewer_security_warning():
    reviewer = CodeReviewer()
    changes = [
        FileChangeRecord(
            file_path="dangerous.py",
            action="created",
            content_before=None,
            content_after="eval('import os; os.system(\"rm -rf /\")')"
        )
    ]
    res = reviewer.review_changes(changes)
    assert res.approved is False
    assert len(res.security_warnings) > 0
    assert res.score < 0.8
