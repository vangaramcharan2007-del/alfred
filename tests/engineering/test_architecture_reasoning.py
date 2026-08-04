from __future__ import annotations

from pathlib import Path
from jarvisx.engineering.planning import ArchitectureReasoner, EngineeringPlan


def test_architecture_reasoning_generates_plan_before_coding(tmp_path: Path) -> None:
    # 1. Setup minimal target structure
    db_file = tmp_path / "src" / "db"
    db_file.mkdir(parents=True, exist_ok=True)
    (db_file / "models.py").write_text("import sqlite3\n\nconn = sqlite3.connect('local.db')\n", encoding="utf-8")

    # 2. Invoke ArchitectureReasoner without modifying code
    reasoner = ArchitectureReasoner(tmp_path)
    plan = reasoner.plan_mission("Replace SQLite with PostgreSQL")

    # 3. Validate plan attributes
    assert plan.goal == "Replace SQLite with PostgreSQL"
    assert len(plan.requirements) > 0
    assert len(plan.assumptions) > 0
    assert len(plan.architecture_decisions) > 0
    assert len(plan.implementation_order) > 0
    assert plan.rollback_strategy != ""
    assert len(plan.risk_assessment) > 0

    report = plan.generate_report()
    assert "ENGINEERING PLAN: Replace SQLite with PostgreSQL" in report
    assert "Requirements:" in report
    assert "Architecture Decisions:" in report
    assert "Rollback Strategy:" in report
