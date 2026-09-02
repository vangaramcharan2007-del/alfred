"""
Smart Interrupt Priority System.
Filters notifications into CRITICAL, IMPORTANT, and NORMAL priority levels.
Prevents notification spam and respects Focus / Study Mode settings.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
from friday.notifier import notify


class SmartInterruptManager:
    """
    Manages proactive notifications based on priority and user context.
    """

    def __init__(self):
        self.focus_mode_active = False
        self.notification_history: List[Dict[str, Any]] = []

    def set_focus_mode(self, active: bool):
        self.focus_mode_active = active

    def dispatch_notification(self, title: str, message: str, priority: str = "NORMAL") -> Dict[str, Any]:
        p_upper = priority.upper()

        if p_upper == "CRITICAL":
            should_deliver = True
        elif p_upper == "IMPORTANT":
            should_deliver = True  # Always deliver important alerts
        elif p_upper == "NORMAL":
            should_deliver = not self.focus_mode_active  # Suppress normal alerts during focus mode
        else:
            should_deliver = not self.focus_mode_active

        delivered = False
        if should_deliver:
            delivered = notify(f"[{p_upper}] {title}", message)

        record = {
            "title": title,
            "message": message,
            "priority": p_upper,
            "delivered": delivered,
            "focus_mode": self.focus_mode_active
        }
        self.notification_history.append(record)

        return {
            "status": "DELIVERED" if delivered else "SUPPRESSED",
            "priority": p_upper,
            "focus_mode_active": self.focus_mode_active,
            "record": record
        }
