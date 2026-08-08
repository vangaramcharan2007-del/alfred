"""Prediction Engine (Future Trajectory Simulator) for Phase 95."""

from __future__ import annotations
import math
from typing import Dict, Any, List, Optional
from jarvisx.proactive.models import TrajectoryForecast
from jarvisx.proactive.proactive_memory import ProactiveMemory


class PredictionEngine:
    """Simulates future academic and engineering outcomes based on current pace and study trajectories."""

    def __init__(self, memory: Optional[ProactiveMemory] = None):
        self.memory = memory or ProactiveMemory()

    def simulate_trajectory(
        self,
        subject: str,
        current_mastery_pct: float,
        weekly_hours: float,
        days_to_exam: int = 30,
        target_score_pct: float = 95.0,
    ) -> TrajectoryForecast:
        """Forecast expected exam score and compute required hours/week needed for 10 CGPA."""
        weeks_left = max(days_to_exam / 7.0, 1.0)

        # Baseline growth: +4.0% mastery per weekly hour studied
        projected_growth = weekly_hours * weeks_left * 4.0
        forecast_score = min(round(current_mastery_pct + projected_growth, 1), 100.0)

        # Calculate required study intensity to hit target
        gap = max(target_score_pct - current_mastery_pct, 0.0)
        required_hours = round(gap / (weeks_left * 4.0), 1)

        # Estimated CGPA impact
        cgpa_delta = round((forecast_score - current_mastery_pct) * 0.12, 1)

        explanation = (
            f"At your current study pace ({weekly_hours}h/week), {subject} is forecasted to reach {forecast_score}% "
            f"by exam day in {days_to_exam} days. To achieve the 95% target, increase study pace to {required_hours}h/week "
            f"(Estimated trajectory boost: +{cgpa_delta}% CGPA)."
        )

        forecast = TrajectoryForecast(
            subject_or_goal=subject,
            current_mastery_pct=current_mastery_pct,
            current_weekly_hours=weekly_hours,
            days_to_target=days_to_exam,
            forecasted_score_pct=forecast_score,
            required_hours_per_week=required_hours,
            cgpa_impact_delta=cgpa_delta,
            explanation=explanation,
        )

        self.memory.save_prediction(forecast)
        return forecast
