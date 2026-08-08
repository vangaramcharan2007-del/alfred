"""Unit Tests for Phase 95: Proactive Intelligence Engine."""

import pytest
import time
from pathlib import Path
from jarvisx.proactive.models import RiskSignal, SignalType, InitiativeType
from jarvisx.proactive.proactive_memory import ProactiveMemory
from jarvisx.proactive.context_monitor import ContextMonitor
from jarvisx.proactive.prediction_engine import PredictionEngine
from jarvisx.proactive.initiative_engine import InitiativeEngine
from jarvisx.proactive.daily_briefing import DailyBriefingGenerator
from jarvisx.proactive.proactive_engine import ProactiveEngine


def test_proactive_memory_persistence_and_schema_version():
    db_file = "var/test_proactive/test_mem.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = ProactiveMemory(db_file)
    sig = RiskSignal(
        id="sig_test_1",
        type=SignalType.ACADEMIC_RISK,
        source="Java Polymorphism",
        severity=75.0,
        confidence=0.92,
        reason=["Mastery 38%", "Exam in 11 days"],
        timestamp=time.time(),
        is_suppressed=False,
    )
    mem.save_risk_signal(sig)

    # Reconnect to same DB
    new_mem = ProactiveMemory(db_file)
    signals = new_mem.list_risk_signals()
    assert len(signals) == 1
    assert signals[0].source == "Java Polymorphism"
    assert signals[0].confidence == 0.92


def test_context_monitor_and_vacation_override_false_positive():
    db_file = "var/test_proactive/test_monitor.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = ProactiveMemory(db_file)
    monitor = ContextMonitor(proactive_mem=mem)

    # Normal sweep
    signals = monitor.scan_for_risks(vacation_override=False)
    assert len(signals) >= 1
    assert any(s.is_suppressed is False for s in signals)

    # Vacation sweep -> false positive emergency alert suppression
    vacation_signals = monitor.scan_for_risks(vacation_override=True)
    assert all(s.is_suppressed is True for s in vacation_signals)


def test_prediction_engine_trajectory_simulation():
    predictor = PredictionEngine()
    forecast = predictor.simulate_trajectory(
        subject="Java & OOP",
        current_mastery_pct=45.0,
        weekly_hours=1.5,
        days_to_exam=28,
        target_score_pct=95.0,
    )
    assert forecast.forecasted_score_pct > 45.0
    assert forecast.required_hours_per_week > 0.0
    assert forecast.cgpa_impact_delta > 0.0
    assert "trajectory" in forecast.explanation.lower()


def test_initiative_engine_confidence_boundaries():
    initiative = InitiativeEngine()

    high_conf = RiskSignal("s1", SignalType.ACADEMIC_RISK, "Java", 80.0, 0.95, ["Failed quiz"], time.time(), False)
    mod_conf = RiskSignal("s2", SignalType.HABIT_DRIFT, "Habit", 60.0, 0.65, ["Streak broke"], time.time(), False)
    low_conf = RiskSignal("s3", SignalType.SCHEDULE_CONFLICT, "Meeting", 40.0, 0.40, ["Uncertain"], time.time(), False)

    decisions = initiative.evaluate_signals_and_decide([high_conf, mod_conf, low_conf])
    assert len(decisions) == 3

    assert decisions[0].action_type == InitiativeType.AUTO_DISPATCH
    assert decisions[1].action_type == InitiativeType.SUGGEST_RECOVERY
    assert decisions[2].action_type == InitiativeType.ASK_CLARIFICATION


def test_proactive_sweep_and_mission_handshake():
    engine = ProactiveEngine()
    res = engine.sweep_and_dispatch()
    assert res["status"] == "SWEEP_COMPLETED"
    assert res["signals_detected"] >= 1
    assert res["dispatched_missions"] >= 1
