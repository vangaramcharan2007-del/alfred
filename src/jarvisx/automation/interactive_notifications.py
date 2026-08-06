"""Interactive Notification Engine for Jarvis X (Layer 4 - Automation).

Extends RealNotificationEngine to support interactive toast prompts and confirmation callbacks.
"""

from typing import Any, Dict, Optional, Callable

from jarvisx.automation.real_notifications import RealNotificationEngine


class InteractiveNotificationEngine:
    """Zero-fluff production interactive desktop notification engine."""

    def __init__(self, base_notifier: Optional[RealNotificationEngine] = None):
        self.base_notifier = base_notifier or RealNotificationEngine()
        self.pending_confirmations: Dict[str, Dict[str, Any]] = {}

    def send_interactive_confirmation(
        self,
        title: str,
        message: str,
        callback_action: Optional[Callable[[], Any]] = None,
        timeout_seconds: int = 5,
    ) -> Dict[str, Any]:
        """Dispatch interactive notification prompt requiring confirmation."""
        # 1. Send native desktop alert toast
        base_res = self.base_notifier.send_desktop_alert(
            title=f"⚠️ {title}",
            message=message,
            timeout_seconds=timeout_seconds,
        )

        conf_id = f"conf_{len(self.pending_confirmations) + 1}"
        record = {
            "conf_id": conf_id,
            "title": title,
            "message": message,
            "status": "PENDING_CONFIRMATION",
            "callback": callback_action,
        }
        self.pending_confirmations[conf_id] = record

        return {
            "status": "PROMPT_DISPATCHED",
            "conf_id": conf_id,
            "base_notification": base_res,
            "details": f"Interactive prompt '{title}' dispatched requiring user confirmation.",
        }

    def confirm_action(self, conf_id: str) -> Dict[str, Any]:
        """Execute confirmation callback for pending action."""
        record = self.pending_confirmations.get(conf_id)
        if not record:
            return {"status": "error", "reason": f"Confirmation ID '{conf_id}' not found"}

        record["status"] = "USER_CONFIRMED"
        cb_res = None
        if record["callback"]:
            try:
                cb_res = record["callback"]()
            except Exception as e:
                cb_res = {"error": str(e)}

        return {
            "status": "CONFIRMED",
            "conf_id": conf_id,
            "action_title": record["title"],
            "callback_result": cb_res,
        }
