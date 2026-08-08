"""Master Proactive Intelligence Engine for Jarvis X (Phase 95)."""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.proactive.models import InitiativeDecision, InitiativeType, RiskSignal, TrajectoryForecast
from jarvisx.proactive.proactive_memory import ProactiveMemory
from jarvisx.proactive.context_monitor import ContextMonitor
from jarvisx.proactive.prediction_engine import PredictionEngine
from jarvisx.proactive.initiative_engine import InitiativeEngine
from jarvisx.proactive.daily_briefing import DailyBriefingGenerator


class ProactiveEngine:
    """Master Proactive Intelligence Coordinator.
    Scans context -> Simulates trajectories -> Evaluates initiative rules -> Dispatches missions.
    """

    def __init__(self):
        self.memory = ProactiveMemory()
        self.monitor = ContextMonitor(proactive_mem=self.memory)
        self.predictor = PredictionEngine(self.memory)
        self.initiative = InitiativeEngine(self.memory)
        self.briefing = DailyBriefingGenerator()

    def status(self) -> List[RiskSignal]:
        """List active risk signals and severity ratings."""
        signals = self.monitor.scan_for_risks()
        print(f"\n[PROACTIVE SENSOR]: Active Risk Signals ({len(signals)} detected)")
        for s in signals:
            flag = "[SUPPRESSED]" if s.is_suppressed else "[ACTIVE]"
            print(f"  • {s.source} (Severity: {s.severity}/100, Confidence: {int(s.confidence*100)}%) {flag}")
            for r in s.reason:
                print(f"      - {r}")
        return signals

    def predict(self) -> List[TrajectoryForecast]:
        """Compute future mastery forecasts and required weekly study hours."""
        signals = self.monitor.scan_for_risks()
        forecasts = []
        for s in signals:
            # Simulate trajectory
            f = self.predictor.simulate_trajectory(
                subject=s.source,
                current_mastery_pct=100.0 - s.severity,
                weekly_hours=1.5,
                days_to_exam=28,
            )
            forecasts.append(f)

        print(f"\n[PROACTIVE PREDICTION]: Future Trajectory Simulations")
        for f in forecasts:
            print(f"  • {f.subject_or_goal}: Projected Score {f.forecasted_score_pct}%")
            print(f"    Required Pace: {f.required_hours_per_week}h/week (+{f.cgpa_impact_delta}% CGPA impact)")
        return forecasts

    def morning(self, user_name: str = "Forgeman") -> Dict[str, Any]:
        """Generate morning Alfred executive briefing."""
        signals = self.monitor.scan_for_risks()
        decisions = self.initiative.evaluate_signals_and_decide(signals)
        forecasts = self.predict()
        res = self.briefing.format_morning_briefing(decisions, forecasts, user_name)
        print(f"\n{res['briefing_text']}\n")
        return res

    def explain(self) -> List[Dict[str, Any]]:
        """Explain reasoning behind each proactive initiative."""
        signals = self.monitor.scan_for_risks()
        decisions = self.initiative.evaluate_signals_and_decide(signals)
        explanations = []
        print(f"\n[PROACTIVE EXPLAINABILITY]: Initiative Reasoning")
        for d in decisions:
            entry = {
                "title": d.title,
                "action_type": d.action_type.value,
                "confidence": d.confidence,
                "reason": d.reason,
            }
            print(f"  • [{d.action_type.value}] {d.title}")
            print(f"    Confidence: {int(d.confidence*100)}%")
            print(f"    Reasoning: {d.reason}")
            explanations.append(entry)
        return explanations

    def sweep_and_dispatch(self) -> Dict[str, Any]:
        """Scan context, filter high-confidence initiatives, and autonomously dispatch to Mission Runtime!"""
        signals = self.monitor.scan_for_risks()
        decisions = self.initiative.evaluate_signals_and_decide(signals)
        dispatched_count = 0

        from jarvisx.agents.agent_executor import AutonomousAgentExecutor
        executor = AutonomousAgentExecutor()

        results = []
        for d in decisions:
            if d.action_type == InitiativeType.AUTO_DISPATCH and d.mission_goal:
                print(f"\n[PROACTIVE DISPATCH]: Taking Autonomous Initiative for '{d.title}'")
                m_res = executor.execute_mission(d.mission_goal)
                d.dispatched = True
                self.memory.save_initiative(d)
                dispatched_count += 1
                results.append({"initiative": d.title, "result": m_res})

        return {
            "status": "SWEEP_COMPLETED",
            "signals_detected": len(signals),
            "initiatives_evaluated": len(decisions),
            "dispatched_missions": dispatched_count,
            "results": results,
        }
