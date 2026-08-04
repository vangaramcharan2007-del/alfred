from __future__ import annotations

from pathlib import Path
from jarvisx.engineering.intelligence import ProjectIntelligence, RepositoryInfo


def test_repository_analysis_on_real_repo(tmp_path: Path) -> None:
    # 1. Create a simulated realistic repository structure in tmp_path
    src_dir = tmp_path / "src" / "sample_app"
    src_dir.mkdir(parents=True, exist_ok=True)
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir(exist_ok=True)

    main_py = src_dir / "main.py"
    main_py.write_text("import fastapi\nimport uvicorn\n\ndef run():\n    pass\n", encoding="utf-8")
    
    test_py = tests_dir / "test_app.py"
    test_py.write_text("import pytest\n\ndef test_dummy():\n    assert True\n", encoding="utf-8")

    req_txt = tmp_path / "requirements.txt"
    req_txt.write_text("fastapi>=0.100.0\nuvicorn\npytest\n", encoding="utf-8")
    
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM python:3.11-slim\nCOPY . /app\n", encoding="utf-8")

    # 2. Perform intelligence inspection
    intel = ProjectIntelligence(tmp_path)
    info = intel.analyze()

    # 3. Verify assertions against real findings
    assert "Python" in info.languages
    assert "FastAPI" in info.frameworks
    assert "pytest" in info.frameworks or "Uvicorn" in info.frameworks
    assert info.package_manager in {"Pip", "Pip / pyproject.toml"}
    assert "Dockerfile" in info.docker_usage
    assert any("main.py" in str(ep) for ep in info.entry_points)
    
    report = info.generate_report()
    assert "ENGINEERING REPORT" in report
    assert "Languages:" in report
    assert "Frameworks:" in report
    assert "Risk Areas:" in report
