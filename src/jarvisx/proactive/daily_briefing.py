"""Daily Morning Executive Briefing for Phase 95."""

from __future__ import annotations
from typing import Dict, Any, List
from jarvisx.proactive.models import InitiativeDecision, InitiativeType, TrajectoryForecast


class DailyBriefingGenerator:
    """Generates the morning Alfred executive briefing text and voice payload."""

    def format_morning_briefing(
        self,
        initiatives: List[InitiativeDecision],
        predictions: List[TrajectoryForecast],
        user_name: str = "Forgeman"
    ) -> Dict[str, Any]:
        """Synthesize formatted executive briefing."""
        critical = [i for i in initiatives if i.action_type == InitiativeType.AUTO_DISPATCH]
        warnings = [i for i in initiatives if i.action_type == InitiativeType.SUGGEST_RECOVERY]

        lines = [
            "=" * 50,
            f"GOOD MORNING {user_name.upper()}",
            "=" * 50,
            "\nMISSION STATUS & ACTIVE INITIATIVES\n",
        ]

        if critical:
            lines.append("[!] Critical Actions (Autonomous Initiative Ready):")
            for c in critical:
                lines.append(f"  • {c.title}")
                lines.append(f"    Reason: {c.reason}")
            lines.append("")

        if warnings:
            lines.append("[!] Warnings & Habit Drift:")
            for w in warnings:
                lines.append(f"  • {w.title}")
                lines.append(f"    Suggestion: {w.reason}")
            lines.append("")

        if predictions:
            lines.append("[+] Trajectory Simulation & Academic Forecast:")
            for p in predictions:
                lines.append(f"  • {p.subject_or_goal}: Forecasted score {p.forecasted_score_pct}%")
                lines.append(f"    Recommendation: {p.required_hours_per_week}h/week needed (+{p.cgpa_impact_delta}% CGPA impact)")
            lines.append("")

        lines.append("=" * 50)
        full_text = "\n".join(lines)

        return {
            "status": "SUCCESS",
            "briefing_text": full_text,
            "critical_count": len(critical),
            "warning_count": len(warnings),
            "prediction_count": len(predictions),
        }
