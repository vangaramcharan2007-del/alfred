"""ASCII Formatters and Visual Telemetry Reporters for Phase 105 Operating Loop."""

from __future__ import annotations
import time
from typing import List

from jarvisx.operating_loop.models import (
    LearningProfile,
    OperatingCycleResult,
    StudyMission,
    TopicMastery,
)


def format_coach_status(profile: LearningProfile) -> str:
    """Format academic coaching profile and topic mastery matrix into clean ASCII table."""
    lines = [
        "================================================================================",
        "                     JARVIS X ACADEMIC & ENGINEERING COACH                      ",
        "================================================================================",
        f"  Degree & Domain : {profile.degree} in {profile.domain}",
        f"  Primary Target  : {profile.primary_goal}",
        f"  Learning Style  : {profile.learning_style}",
        f"  Active Streak   : {profile.active_streak_days} days",
        "--------------------------------------------------------------------------------",
        " TOPIC MASTERY & PRIORITY MATRIX:",
        f"  {'TOPIC NAME':<26} {'DOMAIN':<18} {'MASTERY':<10} {'EXAM':<8} {'PRIORITY':<8}",
        f"  {'-'*26} {'-'*18} {'-'*10} {'-'*8} {'-'*8}",
    ]

    sorted_topics = sorted(
        profile.topics.values(),
        key=lambda t: t.calculate_priority_score(),
        reverse=True,
    )

    for t in sorted_topics:
        m_bar = f"{int(t.mastery_level * 100)}%"
        exam_str = f"{t.exam_proximity_days}d" if t.exam_proximity_days is not None else "--"
        p_score = f"{t.calculate_priority_score():.3f}"
        lines.append(f"  {t.topic_name:<26} {t.domain:<18} {m_bar:<10} {exam_str:<8} {p_score:<8}")

    lines.extend([
        "================================================================================",
    ])
    return "\n".join(lines)


def format_study_plan(missions: List[StudyMission]) -> str:
    """Format prioritized study missions into structured ASCII plan."""
    date_str = time.strftime("%A, %B %d, %Y")
    lines = [
        "================================================================================",
        f"                    JARVIS X STUDY MISSIONS - {date_str}                       ",
        "================================================================================",
    ]

    if not missions:
        lines.append("  No active study missions generated. All topics at target mastery.")
    else:
        for idx, m in enumerate(missions, 1):
            lines.extend([
                f" [{idx}] {m.title}",
                f"     Duration : ~{m.estimated_minutes} minutes",
                f"     Reason   : {m.reason}",
                "     Tasks    :",
            ])
            for t in m.tasks:
                lines.append(f"       [ ] {t}")
            lines.append("")

    lines.append("================================================================================")
    return "\n".join(lines)


def format_loop_trace(cycle: OperatingCycleResult) -> str:
    """Format full 8-stage operating cycle trace."""
    lines = [
        "================================================================================",
        f"          OPERATING LOOP CYCLE TELEMETRY TRACE: {cycle.cycle_id}               ",
        "================================================================================",
        f"  Status       : {cycle.status} (Latency: {cycle.total_latency_ms}ms)",
        f"  1. OBSERVE   : Trigger={cycle.observe.get('trigger_event')} | Topics={cycle.observe.get('monitored_topics_count')}",
        f"  2. UNDERSTAND: Goal='{cycle.understand.get('primary_goal')}' | Risk='{cycle.understand.get('risk_assessment')}'",
        f"  3. DECIDE    : Decision={cycle.decide.get('decision')} | Score={cycle.decide.get('initiative_score')}",
        f"  4. PLAN      : Missions={cycle.plan.get('generated_missions_count')}",
        f"  5. EXECUTE   : Workspaces={cycle.execute.get('prepared_study_workspaces')} | Status={cycle.execute.get('status')}",
        f"  6. EVALUATE  : Coherence={cycle.evaluate.get('plan_coherence_score')} | Verdict={cycle.evaluate.get('verdict')}",
        f"  7. REMEMBER  : Memory={cycle.remember.get('memory_key')} | Streak={cycle.remember.get('streak_reinforced')}",
        f"  8. IMPROVE   : Update='{cycle.improve.get('playbook_update')}'",
        "================================================================================",
    ]
    return "\n".join(lines)
