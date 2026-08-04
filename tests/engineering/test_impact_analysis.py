from __future__ import annotations

from pathlib import Path
from jarvisx.engineering.impact_analyzer import ImpactAnalyzer


def test_impact_analysis_risk_classification(tmp_path: Path) -> None:
    # 1. Create a simulated coupled architecture
    core_file = tmp_path / "core.py"
    core_file.write_text(
        "__all__ = ['shared_func', 'BaseModel']\n\n"
        "class BaseModel:\n"
        "    pass\n\n"
        "def shared_func():\n"
        "    return 'Core functionality'\n",
        encoding="utf-8"
    )

    for i in range(1, 6):
        (tmp_path / f"service_{i}.py").write_text(f"import core\n\ndef execute_{i}():\n    return core.shared_func()\n", encoding="utf-8")
        (tmp_path / f"test_service_{i}.py").write_text(f"import core\nimport service_{i}\n\ndef test_{i}():\n    assert service_{i}.execute_{i}() == 'Core functionality'\n", encoding="utf-8")

    leaf_file = tmp_path / "standalone_leaf.py"
    leaf_file.write_text("def ping():\n    return 'pong'\n", encoding="utf-8")

    analyzer = ImpactAnalyzer(tmp_path)

    # 2. Test HIGH risk on core.py
    report_core = analyzer.analyze_file("core.py")
    assert report_core.breaking_change_risk == "HIGH"
    assert len(report_core.importing_modules) >= 5
    assert len(report_core.dependent_tests) >= 5
    assert any("shared_func" in api for api in report_core.public_apis_affected)
    assert any("HIGH risk" in ev for ev in report_core.supporting_evidence)

    # 3. Test LOW risk on standalone_leaf.py
    report_leaf = analyzer.analyze_file("standalone_leaf.py")
    assert report_leaf.breaking_change_risk in {"LOW", "MEDIUM"} # Depends on API count, with 1 function it's LOW
    assert len(report_leaf.importing_modules) == 0
    
    output = report_core.generate_report()
    assert "IMPACT ANALYSIS REPORT" in output
    assert "Breaking-Change Risk: HIGH" in output
