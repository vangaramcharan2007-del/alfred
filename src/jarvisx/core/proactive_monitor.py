from __future__ import annotations

import asyncio
import time
from typing import Optional, Dict, Any, List

from jarvisx.core.hermes import HermesBus, Event
from jarvisx.tools.personalization import PersonalizationTool
from jarvisx.tools.operational_db import OperationalDatabase


class ProactiveIntelligenceMonitor:
    """
    Monitors system state and user interactions to provide proactive suggestions,
    alerts, and encouragement without being distracting.
    Adheres to the Proactive Intelligence Model.
    """
    
    # Cooldowns in seconds
    COOLDOWNS = {
        "critical": 0,
        "important": 120 * 60,
        "suggestion": 360 * 60,
        "encouragement": 1440 * 60,
    }

    def __init__(
        self,
        hermes: HermesBus,
        personalization: PersonalizationTool,
        op_db: OperationalDatabase,
        check_interval_seconds: int = 60
    ):
        self.hermes = hermes
        self.personalization = personalization
        self.op_db = op_db
        self.check_interval = check_interval_seconds
        
        self._running = False
        self._last_notified: Dict[str, float] = {
            "critical": 0.0,
            "important": 0.0,
            "suggestion": 0.0,
            "encouragement": 0.0
        }

    def start(self) -> asyncio.Task:
        self._running = True
        return asyncio.create_task(self._monitor_loop())

    def stop(self) -> None:
        self._running = False

    async def _monitor_loop(self) -> None:
        while self._running:
            try:
                await self._evaluate_proactive_state()
            except Exception as e:
                # Log silently
                pass
            await asyncio.sleep(self.check_interval)

    async def _evaluate_proactive_state(self) -> None:
        mode_res = self.personalization.get_mode()
        if not mode_res.success:
            return
            
        mode = mode_res.data.get("mode", "companion")
        now = time.time()
        
        # 1. Critical Checks (No cooldown)
        if self._can_notify("critical", mode, now):
            # Check for critical issues like provider outages, workflow failures
            critical_msg = self._check_critical_issues()
            if critical_msg:
                self._send_proactive_message(critical_msg, "critical")
                self._last_notified["critical"] = now
                
        # 2. Important Checks (120 min cooldown)
        if self._can_notify("important", mode, now):
            important_msg = self._check_important_issues()
            if important_msg:
                self._send_proactive_message(important_msg, "important")
                self._last_notified["important"] = now
                
        # 3. Suggestions Checks (360 min cooldown)
        if self._can_notify("suggestion", mode, now):
            suggestion_msg = self._check_suggestions()
            if suggestion_msg:
                self._send_proactive_message(suggestion_msg, "suggestion")
                self._last_notified["suggestion"] = now
                
        # 4. Encouragement Checks (1440 min cooldown)
        if self._can_notify("encouragement", mode, now):
            encouragement_msg = self._check_encouragement()
            if encouragement_msg:
                self._send_proactive_message(encouragement_msg, "encouragement")
                self._last_notified["encouragement"] = now

    def _can_notify(self, category: str, mode: str, now: float) -> bool:
        """Evaluate if we are allowed to send a notification for this category based on mode and cooldown."""
        # Check Mode constraints
        if mode in ("sleep", "do_not_disturb"):
            if category != "critical":
                return False
        elif mode == "focus":
            if category not in ("critical", "important"):
                return False
                
        # Builder mode specifically enables workflow recommendations (suggestions)
        
        # Check Cooldown
        time_since_last = now - self._last_notified.get(category, 0)
        cooldown_needed = self.COOLDOWNS.get(category, 0)
        
        return time_since_last >= cooldown_needed

    def _check_critical_issues(self) -> Optional[str]:
        # Placeholder for provider outages, workflow failures, low battery
        # Example: check op_db for failed workflows
        return None

    def _check_important_issues(self) -> Optional[str]:
        # Placeholder for missed deadlines, inactive projects
        return None

    def _check_suggestions(self) -> Optional[str]:
        # Placeholder for optimization opportunities, study suggestions
        return None

    def _check_encouragement(self) -> Optional[str]:
        # Placeholder for XP milestones, streak achievements
        return None

    def _send_proactive_message(self, message: str, category: str) -> None:
        """Sends the proactive message to Alfred via Hermes."""
        event = Event(
            source="proactive_monitor",
            event_type="proactive_notification",
            payload={
                "message": message,
                "category": category
            }
        )
        self.hermes.publish(event)
