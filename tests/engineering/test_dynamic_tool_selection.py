from __future__ import annotations

from pathlib import Path
from jarvisx.engineering.tooling import DynamicToolSelector, DatabaseMigrationTool, DockerContainerTool


def test_dynamic_tool_selection_and_reasoning(tmp_path: Path) -> None:
    selector = DynamicToolSelector()

    # 1. Test ranking and selection for database migration task
    tool, confidence, reasoning = selector.select_tool("Replace SQLite with PostgreSQL storage layer")
    assert isinstance(tool, DatabaseMigrationTool)
    assert confidence >= 0.50
    assert "Selected capability 'DatabaseMigrationTool'" in reasoning
    assert len(selector.selection_history) == 1
    assert selector.selection_history[0]["tool"] == "DatabaseMigrationTool"

    # 2. Test execution of selected tool on repository
    res = selector.execute_task("Convert project to Docker container deployment", tmp_path)
    assert res.success is True
    assert res.tool_name == "DockerContainerTool"
    assert "Dockerfile" in res.modified_files
    assert (tmp_path / "Dockerfile").exists()
    assert "Selected capability 'DockerContainerTool'" in res.reasoning
