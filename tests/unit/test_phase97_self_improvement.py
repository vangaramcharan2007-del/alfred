"""Unit Tests for Phase 97: Self Improvement Loop."""

import pytest
import time
from pathlib import Path
from jarvisx.self_improvement.models import (
    ErrorClass,
    FailureRootCause,
    PerformanceMetric,
    UpgradeStatus,
)
from jarvisx.self_improvement.self_improvement_memory import SelfImprovementMemory
from jarvisx.self_improvement.performance_analyzer import PerformanceAnalyzer
from jarvisx.self_improvement.failure_root_cause import FailureRootCauseEngine
from jarvisx.self_improvement.pattern_miner import SuccessPatternMiner
from jarvisx.self_improvement.upgrade_manager import UpgradeManager
from jarvisx.self_improvement.self_improvement_engine import SelfImprovementEngine


def test_self_improvement_memory_persistence_and_schema_version():
    db_file = "var/test_improve/test_mem.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = SelfImprovementMemory(db_file)
    metric = PerformanceMetric(
        agent_name="Coder",
        total_tasks=50,
        successes=48,
        failures=2,
        success_rate=0.96,
        avg_duration_sec=0.12,
        confidence_score=0.95,
        trend="UPWARD"
    )
    mem.save_metric(metric)

    new_mem = SelfImprovementMemory(db_file)
    metrics = new_mem.list_metrics()
    assert len(metrics) == 1
    assert metrics[0].agent_name == "Coder"
    assert metrics[0].success_rate == 0.96


def test_performance_analyzer_agent_scorecards_and_trends():
    db_file = "var/test_improve/test_perf.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = SelfImprovementMemory(db_file)
    analyzer = PerformanceAnalyzer(mem)
    summary = analyzer.get_scorecard_summary()

    assert summary["total_agents"] == 4
    assert summary["fleet_success_rate"] > 90.0
    assert any(m["agent_name"] == "AlfredMaster" for m in summary["metrics"])


def test_failure_root_cause_diagnosis_and_recurrence():
    db_file = "var/test_improve/test_fail.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = SelfImprovementMemory(db_file)
    engine = FailureRootCauseEngine(mem)

    r1 = engine.diagnose_failure(
        error_class=ErrorClass.BAD_DELEGATION,
        failed_agent="AlfredMaster",
        error_message="Missing OpenAPI schemas"
    )
    assert r1.recurrence_count == 1

    r2 = engine.diagnose_failure(
        error_class=ErrorClass.BAD_DELEGATION,
        failed_agent="AlfredMaster",
        error_message="Missing OpenAPI schemas again"
    )
    assert r2.recurrence_count == 2
    assert "precondition" in r2.proposed_fix.lower()


def test_success_pattern_miner_playbooks():
    db_file = "var/test_improve/test_pat.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = SelfImprovementMemory(db_file)
    miner = SuccessPatternMiner(mem)
    playbooks = miner.get_playbooks()

    assert len(playbooks) >= 3
    assert any(p.task_type == "fastapi_microservice" for p in playbooks)
    assert any(p.success_rate >= 0.90 for p in playbooks)


def test_upgrade_manager_sandbox_validation_and_rollback():
    db_file = "var/test_improve/test_upg.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = SelfImprovementMemory(db_file)
    mgr = UpgradeManager(mem)

    # 1. Normal upgrade pass
    prop = mgr.propose_upgrade(
        target_component="CodingAgent",
        change_type="PROMPT_AST_CHECK",
        patch_diff="+ ast.parse validation",
        rollback_plan="git checkout main -- src/jarvisx/multi_agent/coding_agent.py"
    )
    assert prop.status == UpgradeStatus.PROPOSED

    run = mgr.run_sandbox_validation(prop, simulate_regression=False)
    assert run.status == "PASSED"
    assert prop.status == UpgradeStatus.VALIDATED

    apply_res = mgr.apply_upgrade(prop)
    assert apply_res["status"] == "SUCCESS"
    assert prop.status == UpgradeStatus.APPLIED

    # 2. Rollback test
    rb_res = mgr.rollback_upgrade(prop)
    assert rb_res["status"] == "ROLLED_BACK"
    assert prop.status == UpgradeStatus.ROLLED_BACK

    # 3. Regression rejection test
    bad_prop = mgr.propose_upgrade("Friday", "UNSAFE_CHANGE", "+ rm -rf", "git checkout")
    bad_run = mgr.run_sandbox_validation(bad_prop, simulate_regression=True)
    assert bad_run.status == "REJECTED"
    assert bad_prop.status == UpgradeStatus.REJECTED
