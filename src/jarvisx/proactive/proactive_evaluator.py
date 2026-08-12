"""Bounded Autonomous Proactive Evaluator for Jarvis X.

Coordinates background evaluation:
1. Observes state (goals, deadlines, system health, user memory).
2. Uses LLMRouter to decide whether a proactive intervention is necessary.
3. Enforces strict bounds: duplicate suppression, cooldowns, and non-interactive permission gates.
4. Routes approved actions through ToolExecutor.
5. Persists auditable intervention outcomes.
"""

from __future__ import annotations
import dataclasses
import hashlib
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from jarvisx.llm.llm_router import LLMRouter
from jarvisx.personal_os.goal_manager import GoalManager
from jarvisx.personal_os.models import GoalStatus
from jarvisx.proactive.proactive_memory import ProactiveMemory
from jarvisx.tools.tool_executor import ToolExecutor
from jarvisx.tools.tool_kernel import ToolRegistry
from jarvisx.tools.builtin_tools import register_builtin_tools

logger = logging.getLogger("jarvisx.proactive_evaluator")


@dataclasses.dataclass
class ProactiveEvaluationResult:
    """Structured decision contract for bounded proactive interventions."""
    should_intervene: bool
    intervention_type: str = "none"
    reason: str = ""
    priority: str = "low"
    message: str = ""
    action: Optional[Dict[str, Any]] = None
    action_result: Optional[Dict[str, Any]] = None
    outcome: str = "no_intervention"
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class ProactiveEvaluator:
    """Bounded, safe background evaluator for study reminders, goal check-ins, and system health alerts."""

    DEFAULT_COOLDOWNS = {
        "study_reminder": 14400.0,  # 4 hours
        "goal_checkin": 21600.0,   # 6 hours
        "system_health": 3600.0,    # 1 hour
    }

    def __init__(
        self,
        proactive_memory: Optional[ProactiveMemory] = None,
        goal_manager: Optional[GoalManager] = None,
        memory_engine: Optional[Any] = None,
        llm_router: Optional[LLMRouter] = None,
        tool_executor: Optional[ToolExecutor] = None,
        cooldowns: Optional[Dict[str, float]] = None,
    ):
        self.proactive_memory = proactive_memory or ProactiveMemory()
        self.goal_manager = goal_manager or GoalManager()
        self.memory_engine = memory_engine
        self.llm_router = llm_router or LLMRouter()

        registry = ToolRegistry.get_instance()
        if not registry.list_tools():
            register_builtin_tools(registry)
        self.tool_executor = tool_executor or ToolExecutor(registry=registry)

        self.cooldowns = dict(self.DEFAULT_COOLDOWNS)
        if cooldowns:
            self.cooldowns.update(cooldowns)

    def evaluate_cycle(self, now: Optional[float] = None, force: bool = False) -> ProactiveEvaluationResult:
        """Run one bounded evaluation cycle across goals, memory, and system state."""
        current_time = now if now is not None else time.time()

        # Step 1: Observe Context
        candidate_signals = self._collect_candidate_signals(current_time)
        if not candidate_signals:
            return ProactiveEvaluationResult(
                should_intervene=False,
                intervention_type="none",
                reason="System, goals, and study state are stable. No intervention required.",
                priority="low",
                message="",
                action=None,
                outcome="no_intervention_needed",
                timestamp=current_time,
            )

        # Step 2: LLM Evaluation
        try:
            prompt = self._build_evaluation_prompt(candidate_signals)
            llm_res = self.llm_router.route_request_sync(prompt=prompt)
            out = llm_res.get("result", {})
            response_text = out.get("response", "")

            if not response_text or out.get("status") != "AVAILABLE":
                return ProactiveEvaluationResult(
                    should_intervene=False,
                    reason="LLM provider unavailable for proactive evaluation.",
                    priority="low",
                    outcome="llm_unavailable",
                    timestamp=current_time,
                )
        except Exception as e:
            logger.warning(f"LLM failure during proactive evaluation: {e}")
            return ProactiveEvaluationResult(
                should_intervene=False,
                reason=f"LLM evaluation exception: {e}",
                priority="low",
                outcome="llm_failure_isolated",
                timestamp=current_time,
            )

        # Step 3: Parse Structured Decision
        decision_data = self._parse_llm_decision(response_text)
        if not decision_data:
            return ProactiveEvaluationResult(
                should_intervene=False,
                reason="Malformed LLM proactive decision JSON.",
                priority="low",
                outcome="malformed_decision_rejected",
                timestamp=current_time,
            )

        should_intervene = bool(decision_data.get("should_intervene", False))
        intervention_type = str(decision_data.get("intervention_type", "study_reminder"))
        reason = str(decision_data.get("reason", ""))
        priority = str(decision_data.get("priority", "low"))
        message = str(decision_data.get("message", ""))
        action = decision_data.get("action")

        if not should_intervene:
            return ProactiveEvaluationResult(
                should_intervene=False,
                intervention_type=intervention_type,
                reason=reason or "LLM evaluated no intervention necessary.",
                priority=priority,
                message="",
                action=None,
                outcome="no_intervention",
                timestamp=current_time,
            )

        # Step 4: Cooldown & Duplicate Suppression
        message_hash = hashlib.sha256(message.strip().lower().encode("utf-8")).hexdigest()[:16]
        cooldown_window = self.cooldowns.get(intervention_type, 14400.0)

        last_record = self.proactive_memory.get_last_intervention_time(intervention_type)
        if last_record and not force:
            last_time, last_hash = last_record
            time_elapsed = current_time - last_time

            # Check duplicate message
            if last_hash == message_hash and time_elapsed < cooldown_window:
                logger.info(f"Duplicate intervention suppressed for '{intervention_type}'")
                return ProactiveEvaluationResult(
                    should_intervene=False,
                    intervention_type=intervention_type,
                    reason=f"Duplicate intervention message suppressed ({int(time_elapsed)}s elapsed).",
                    priority=priority,
                    message=message,
                    action=None,
                    outcome="duplicate_suppressed",
                    timestamp=current_time,
                )

            # Check general cooldown
            if time_elapsed < cooldown_window:
                logger.info(f"Intervention cooldown active for '{intervention_type}' ({int(time_elapsed)}s / {int(cooldown_window)}s)")
                return ProactiveEvaluationResult(
                    should_intervene=False,
                    intervention_type=intervention_type,
                    reason=f"Cooldown active for {intervention_type} ({int(time_elapsed)}s elapsed).",
                    priority=priority,
                    message=message,
                    action=None,
                    outcome="cooldown_active",
                    timestamp=current_time,
                )

        # Step 5: Action Execution & Permission Gate
        action_result = None
        if action and isinstance(action, dict) and "tool" in action:
            tool_name = action.get("tool")
            tool_args = action.get("arguments", {})
            try:
                res = self.tool_executor.execute(tool_name, tool_args, interactive=False)
                action_result = res.to_dict()
                if res.status != "success" or not res.verified:
                    outcome = "action_blocked_or_failed"
                    reason = f"{reason} | Tool {tool_name} failed: {res.error}"
                else:
                    outcome = "intervention_executed_with_action"
            except Exception as te:
                action_result = {"status": "failed", "tool": tool_name, "error": str(te), "verified": False}
                outcome = "action_exception"
                reason = f"{reason} | Tool exception: {te}"
        else:
            outcome = "intervention_notified"

        # Step 6: Persist Intervention and Update Cooldown
        intervention_id = f"int_{str(uuid.uuid4())[:8]}"
        self.proactive_memory.save_intervention(
            intervention_id=intervention_id,
            intervention_type=intervention_type,
            reason=reason,
            priority=priority,
            message=message,
            action_json=json.dumps(action) if action else "",
            outcome=outcome,
            timestamp=current_time,
        )
        self.proactive_memory.update_intervention_cooldown(
            intervention_type=intervention_type,
            timestamp=current_time,
            message_hash=message_hash,
        )

        return ProactiveEvaluationResult(
            should_intervene=True,
            intervention_type=intervention_type,
            reason=reason,
            priority=priority,
            message=message,
            action=action,
            action_result=action_result,
            outcome=outcome,
            timestamp=current_time,
        )

    def _collect_candidate_signals(self, current_time: float) -> List[Dict[str, Any]]:
        """Collect potential intervention candidates from goals, deadlines, and system state."""
        signals = []

        # 1. Inspect Goals
        try:
            goals = self.goal_manager.list_goals()
            for g in goals:
                if g.status == GoalStatus.AT_RISK:
                    signals.append({
                        "category": "study_reminder",
                        "title": g.title,
                        "risk_reason": g.risk_reason or "Goal marked AT_RISK",
                        "progress_pct": g.progress_pct,
                        "target_date": g.target_date,
                    })
                elif g.status == GoalStatus.ACTIVE:
                    # Incomplete milestones
                    pending_ms = [m for m in g.milestones if not m.completed]
                    if pending_ms:
                        signals.append({
                            "category": "goal_checkin",
                            "title": g.title,
                            "pending_milestones": [m.title for m in pending_ms[:2]],
                            "progress_pct": g.progress_pct,
                            "target_date": g.target_date,
                        })
        except Exception as ge:
            logger.warning(f"Goal inspection warning: {ge}")

        # 2. Inspect Memory Context (e.g. primary goals / focus)
        if self.memory_engine:
            try:
                pcontext = self.memory_engine.get_personal_context(query="current focus and goals")
                if pcontext and pcontext.goal_alignment:
                    signals.append({
                        "category": "user_preference",
                        "goal_alignment": pcontext.goal_alignment,
                    })
            except Exception as me:
                logger.warning(f"Memory context inspection warning: {me}")

        return signals

    def _build_evaluation_prompt(self, signals: List[Dict[str, Any]]) -> str:
        """Compose structured decision prompt for the LLM."""
        signals_json = json.dumps(signals, indent=2)
        return (
            "You are Alfred, a sovereign AI executive assistant. "
            "Evaluate the following background context and decide if a proactive notification or intervention is necessary.\n\n"
            f"Candidate Context & Signals:\n{signals_json}\n\n"
            "Safety & Decision Rules:\n"
            "1. Default to observe: set 'should_intervene': false unless an intervention is genuinely helpful.\n"
            "2. If an approaching deadline, at-risk objective, or important milestone is pending, generate a concise polite spoken reminder.\n"
            "3. Set 'intervention_type' to one of: 'study_reminder', 'goal_checkin', 'system_health'.\n"
            "4. Do NOT propose destructive actions or shell commands.\n"
            "5. Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "should_intervene": true,\n'
            '  "intervention_type": "study_reminder",\n'
            '  "reason": "<clear justification for intervening>",\n'
            '  "priority": "low" | "medium" | "high",\n'
            '  "message": "<polite spoken reminder to the user>",\n'
            '  "action": null\n'
            "}"
        )

    def _parse_llm_decision(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Safely extract and parse JSON decision from LLM response."""
        text = response_text.strip()
        decoder = json.JSONDecoder()
        idx = 0
        while idx < len(text):
            brace_pos = text.find('{', idx)
            if brace_pos == -1:
                break
            try:
                obj, end_pos = decoder.raw_decode(text[brace_pos:])
                if isinstance(obj, dict) and "should_intervene" in obj:
                    return obj
                idx = brace_pos + 1
            except json.JSONDecodeError:
                idx = brace_pos + 1
        return None
