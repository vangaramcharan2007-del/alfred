import pytest
from jarvisx.capabilities.coding.pipeline.code_executor import FileChangeRecord
from jarvisx.capabilities.coding.change_risk import ChangeRiskAnalyzer

def test_change_risk_low():
    analyzer = ChangeRiskAnalyzer()
    changes = [
        FileChangeRecord(file_path="utils.py", action="modified", content_after="def add(a, b): return a + b")
    ]
    assessment = analyzer.calculate_risk(changes)
    assert assessment.risk_level in ["LOW", "MEDIUM"]

def test_change_risk_high_security():
    analyzer = ChangeRiskAnalyzer()
    changes = [
        FileChangeRecord(file_path="auth_db.py", action="modified", content_after="import os; eval('os.system(\"rm -rf\")')")
    ]
    assessment = analyzer.calculate_risk(changes)
    assert assessment.risk_level == "HIGH"
    assert len(assessment.risk_factors) >= 1
