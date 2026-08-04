from __future__ import annotations

import sys
from pathlib import Path
from jarvisx.engineering.workflow import AdaptiveEngineeringAgent


def test_end_to_end_repository_modification_workflow(tmp_path: Path) -> None:
    # 1. Setup minimal operational repository
    src_dir = tmp_path / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    app_py = src_dir / "app.py"
    app_py.write_text("def run():\n    return 'Hello'\n", encoding="utf-8")

    mem_file = tmp_path / "engineering_mem.jsonl"

    # 2. Instantiate agent and execute modification mission
    agent = AdaptiveEngineeringAgent(tmp_path, memory_path=mem_file)
    report = agent.execute_mission(
        "Convert project to Docker containerization deployment",
        test_cmd=[sys.executable, "-c", "import sys; sys.exit(0)"]
    )

    # 3. Verify mission success and physical artifact modification
    assert report.mission_goal == "Convert project to Docker containerization deployment"
    assert report.tool_execution.success is True
    assert "Dockerfile" in report.tool_execution.modified_files
    assert (tmp_path / "Dockerfile").exists()
    assert report.change_report.success is True
    assert report.change_report.build_clean is True

    summary = report.generate_report()
    assert "ADAPTIVE ENGINEERING WORKFLOW EXECUTION" in summary
    assert "[6. FINAL CHANGE VERIFICATION REPORT]" in summary
    assert "Dockerfile" in summary
